# -*- coding: utf-8 -*-



import asyncio
import aiohttp
import configparser
import colorama
colorama.init()
import backoff
import copy
import random
import os
import zipfile
import re
import bs4
import ssl
from shutil import rmtree
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)
from modules import coloring, logwrite, tools
coloring = coloring.coloring


def ignore_aiohttp_ssl_eror(loop):
	"""Ignore aiohttp #3535 / cpython #13548 issue with SSL data after close

	There is an issue in Python 3.7 up to 3.7.3 that over-reports a
	ssl.SSLError fatal error (ssl.SSLError: [SSL: KRB5_S_INIT] application data
	after close notify (_ssl.c:2609)) after we are already done with the
	connection. See GitHub issues aio-libs/aiohttp#3535 and
	python/cpython#13548.

	Given a loop, this sets up an exception handler that ignores this specific
	exception, but passes everything else on to the previous exception handler
	this one replaces.

	Checks for fixed Python versions, disabling itself when running on 3.7.4+
	or 3.8.

	"""
	# if sys.version_info >= (3, 7, 4):
	# 	return

	orig_handler = loop.get_exception_handler()
	def ignore_ssl_error(loop, context):
		SSL_PROTOCOLS = (asyncio.sslproto.SSLProtocol,)
		try:
			import uvloop.loop
		except ImportError:
			pass
		else:
			SSL_PROTOCOLS = (*SSL_PROTOCOLS, uvloop.loop.SSLProtocol)
		if context.get("message") in {
			"SSL error in data received",
			"Fatal error on transport",
			"SSL handshake failed",
		}:
			# validate we have the right exception, transport and protocol
			exception = context.get('exception')
			protocol = context.get('protocol')
			if (
				isinstance(exception, ssl.SSLError)
				and exception.reason == 'KRB5_S_INIT'
				and isinstance(protocol, SSL_PROTOCOLS)
			):
				if loop.get_debug():
					asyncio.log.logger.debug('Ignoring asyncio SSL KRB5_S_INIT error')
				return
		if orig_handler is not None:
			orig_handler(loop, context)
		else:
			loop.default_exception_handler(context)
	loop.set_exception_handler(ignore_ssl_error)



class Parser(object):
	'''
	Парсер
	'''
	def __init__(self):
		super().__init__()
		try:
			os.mkdir("downloads/")
		except OSError:
			pass
		except Exception as e:
			raise e
		####################
		self.proxies = set()
		self.links = set()
		self.zipLinks = set()
		self.linksForDownload = []
		########################################
		with open("texts/usrAgents.txt") as file:
			self.agents = file.read().split("\n")
			while True:
				try:
					self.agents.remove("")
				except:
					break
		########################################
		self.MAINURLS = ( # сайты, с которых парсится основная часть проксей путем регулярочек и архивов
			"http://www.proxyserverlist24.top/",
			"http://www.socks24.org",
			"http://www.vipsocks24.net/",
			"http://www.socksproxylist24.top/",
			"http://www.sslproxies24.top/"
			)
		self.MAINURLS = set(self.MAINURLS)
		####################################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.TIMEOUT = aiohttp.ClientTimeout(total=30, connect=config.getint("PARSER", "TIMEOUT"))
		self.MAXTRIES = config.getint("PARSER", "MAXTRIES")
		self.TASKS = config.getint("PARSER", "TASKS")

	@tools.errorsCap
	def main(self):
		'''
		Парсер
		'''
		print(self.NAME + coloring("Начался парсинг прокси...", "white"))
		##############################################
		self.inputLinks = copy.deepcopy(self.MAINURLS)
		self.lock = asyncio.Lock()
		loop = asyncio.get_event_loop()
		tasks = []
		ignore_aiohttp_ssl_eror(loop)
		#############################
		# парсинг и анализ ссылок
		for i in range(0, 3):
			##############################
			for i in range(0, self.TASKS):
				tasks.append(loop.create_task(self.getWebPage()))
			####
			try:
				loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
			except KeyboardInterrupt:
				print("\n" + self.NAME + coloring("Парсинг отменен!", "yellow"))
				return self.proxies
			except RuntimeError:
				print("\n" + self.NAME + coloring("Закачка отменена!", "yellow"))
				return self.proxies
			except Exception as e:
				logwrite.log(e, "parser")
			else:
				tools.loopResponse(loop_response, "parser")
			finally:
				# очистка ссылок, если остались
				self.inputLinks.clear()
				# загрузка новых
				self.inputLinks = copy.deepcopy(self.links)
				# очистка напарсенных ссылок
				self.links.clear()
		#########################################
			# получены страницы и ссылки с них
			for i in self.links:
				if "zip" in i:
					self.zipLinks.add(i)
				else:
					self.inputLinks.add(i)
		#########################################
		print(self.NAME + coloring("Анализ найденных ссылок на архивы...", 'green'))
		# тут скачка страниц с самими ссылками на файл
		self.inputLinks = copy.deepcopy(self.zipLinks)
		##############################################
		for i in range(0, self.TASKS):
				tasks.append(loop.create_task(self.getWebPage()))
		#########################################################
		try:
			loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except KeyboardInterrupt:
			print("\n" + self.NAME + coloring("Парсинг отменен!", "yellow"))
			return self.proxies
		except RuntimeError:
			print("\n" + self.NAME + coloring("Закачка отменена!", "yellow"))
			return self.proxies
		except Exception as e:
			logwrite.log(e, "parser archives")
		else:
			tools.loopResponse(loop_response, "parser archives")
		#############################################################
		# тут скачка архивов
		self.inputLinks = copy.deepcopy(self.linksForDownload)
		print(self.NAME + coloring("Загрузка архивов...", "green"))
		#############################################################
		for i in range(0, self.TASKS):
				tasks.append(loop.create_task(self.DownloadArchive()))
		#############################################################
		try:
			loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except KeyboardInterrupt:
			print("\n" + self.NAME + coloring("Проверка отменена! Завершение задач...", "yellow"))
			for i in tasks:
				i.cancel()
			return self.proxies
		except RuntimeError:
			print("\n" + self.NAME + coloring("Закачка отменена!", "yellow"))
			for i in tasks:
				i.cancel()
			return self.proxies
		except Exception as e:
			logwrite.log(e, "download archives")
		else:
			tools.loopResponse(loop_response, "download archives")
		###################################################
		# распаковка и получение проксей
		try:
			self.zipExtractor()
		except Exception as e:
			if "downloads" in os.getcwd():
				os.chdir("..")
			if os.access("downloads", mode=0):
				rmtree("downloads")
			logwrite.log(e, "open archives")
		#################################################################
		print(self.NAME + coloring("Парсинг проксей закончен!", "green"))
		print(self.NAME + coloring(f"Получено {str(len(self.proxies))} проксей, из которых ", "white"), end="")
		self.proxies = [*self.proxies]
		print(coloring(f"{str(len(self.proxies))} уникальные.", "green"))
		#################################################################
		return self.proxies

	@staticmethod
	def getLinks(response):
			'''
			Получение ссылок из html-страницы
			'''
			answer = bs4.BeautifulSoup(response, "lxml")  # создание объекта супа из html страницы
			answer = answer.find_all("a")  # получение всех тегов ссылок
			links = []
			for i in answer:
				link = i.get("href")
				if link and ("#" not in link) and ("blogger.com" not in link) and ("http" in link):
					links.append(link)
				else:
					pass
			random.shuffle(links)
			return links

	def getDownloadLinks(self, response):
		'''
		Получение прямых ссылок для скачивания и добавление их в множество set
		'''
		answer = bs4.BeautifulSoup(response, "lxml")  # создание объекта супа из html страницы
		answer = answer.find_all("a")  # получение всех тегов ссылок
		links = []
		for i in answer:
			link = i.get("href")
			if link and ("#" not in link) and ".zip" in link:
				links.append(link)
			else:
				pass
		random.shuffle(links)
		self.linksForDownload.extend(links)

	@staticmethod
	async def send(url, **kwargs):
		'''
		Отправка GET запроса
		'''
		async with aiohttp.ClientSession(**kwargs) as session:
			async with session.get(url, ssl=False) as response:
				return await response.text()

	@staticmethod
	async def download(url, **kwargs):
		'''
		Скачивание архива
		'''
		async with aiohttp.ClientSession(**kwargs) as session:
			async with session.get(url, ssl=False, allow_redirects=True) as response:
				return await response.read()

	async def getWebPage(self):
		'''
		Асинхронная задача для скачивания и анализа веб-страниц
		'''
		send = backoff.on_exception(backoff.expo, Exception, max_time=60, max_tries=self.MAXTRIES, jitter=None)(self.send)
		send = self.send
		headers = {
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.5",
			"Connection": "close",
		}
		############
		while True:
			###############
			async with self.lock:
				try:
					i = self.inputLinks.pop()
				except:
					break
			headers["User-Agent"] = self.agents[random.randint(0, len(self.agents)-1)]
			###############
			try:
				#print(i)
				response = await send(i, timeout=self.TIMEOUT, headers=headers)
			except KeyboardInterrupt:
				break
			except Exception as e:
				print(self.NAME + coloring(f"[{str(len(self.inputLinks))}]Не удалось скачать страницу {i}", "white"))
			else:
				local_links = self.getLinks(response)
				self.parseProxies(response)
				###############
				async with self.lock:
					self.links.update(local_links)
					self.getDownloadLinks(response)
				###################################
				print(self.NAME +coloring(f"[{str(len(self.inputLinks))}]Спарсена страница {i}", "green"))

	async def DownloadArchive(self):
		'''
		Асинхронная задача для скачивания архивов
		'''
		###############################
		send = backoff.on_exception(backoff.expo, Exception, max_time=60, max_tries=3, jitter=None)(self.download)
		timeout = aiohttp.ClientTimeout(connect=4)
		headers = {
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.5",
			"Connection": "keep-alive",
		}
		###############################
		while True:
			###############
			async with self.lock:
				try:
					i = self.inputLinks.pop()
				except:
					break
			headers["User-Agent"] = self.agents[random.randint(0, len(self.agents)-1)]
			####################################
			try:
				response = await send(i, headers=headers, timeout=timeout)
			except KeyboardInterrupt:
				break
			except Exception as e:
				print(self.NAME + coloring(f"Не удалось загрузить архив {i}", "white"))
			else:
				self.saveArchive(response)

	def zipExtractor(self):
		'''
		Распаковка архивов
		'''
		os.chdir("downloads")
		files = os.listdir()
		########################
		# анализ списка файлов в downloads
		for i in files:
			###################
			# если не зипфайл - пропускать
			if not ".zip" in i:
				os.chmod(i, 0o777)
				os.remove(i)
				continue
			###################
			# открываем зипом и распаковываем
			try:
				xfile = zipfile.ZipFile(i)
				xfile.extractall()
				xfile.close()
			except Exception as e:
				os.remove(i)
				print(self.NAME + coloring(f"Ошибка распаковки архива {i}!", "red"))
				#raise e
				continue
			else:
				print(self.NAME + coloring(f"Удалось успешно распаковать архив {i}", "green"))
			##################
			# получаем список распакованных файлов
			extracted = os.listdir()
			##################
			for l in extracted:
				# получаем прокси из .txt файла
				if ".txt" in l:
					self.loadProxies_(l)
			##################
			# удаляем то, что распаковали
			for j in extracted:
				os.chmod(j, 0o777)
				if ".zip" in j:
					continue
				else:
					try:
						os.remove(j)
					except IsADirectoryError:
						rmtree(j)
					except Exception as e:
						print(self.NAME + coloring(f"Ошибка {e} при удалении файла {j}", "red"))
						logwrite.log(e, "zipExtractor")
			#################
			os.remove(i)
			#################
		os.chdir("..")
		try:
			os.rmdir("downloads")
		except OSError:
			rmtree("downloads")
		except Exception as e:
			logwrite.log(e, "remove downloads")

	def parseProxies(self, string):
		'''
		Парсинг проксей с помощью регулярок из html страницы
		'''
		if not isinstance(string, str):
			string = str(string)
		proxies_find = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", string)
		self.proxies.update(proxies_find)

	def saveArchive(self, content):
		'''
		Сохранение архива
		'''
		filename = os.getcwd() + "/downloads/" + str(random.randint(1, 10000)) + ".zip"
		with open(filename, mode="wb") as file:
			file.write(content)
		os.chmod(filename, 0o777)
		print(self.NAME + coloring(f"Успешно сохранен архив {filename}", "green"))

	def loadProxies_(self, txt):
		'''
		Получения проксей из txt, используется в другом методе
		'''
		with open(txt, mode="r") as file:
			proxies = file.read().split("\n")
			while True:
				try:
					proxies.remove("")
				except:
					break
		print(self.NAME + coloring(f"Получено {str(len(proxies))}.", "green"))
		self.proxies.update(proxies)



if __name__ == '__main__':
	pass