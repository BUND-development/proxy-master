# -*- coding: utf-8 -*-



import asyncio
import aiohttp
from aiohttp_proxy import ProxyConnector
import backoff
import configparser
import copy
from requests import get, exceptions
import json
import random
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)
import colorama
colorama.init()
from modules import coloring, logwrite, tools
coloring = coloring.coloring
import ssl


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



class BoardGetError(exceptions.ConnectionError):
	pass



class BansChecker(object):
	'''
	Проверка на баны
	'''
	def __init__(self, proxies, protocol):
		super().__init__()
		self.proxies = proxies
		self.protocol = protocol
		self.url = "http://5.61.239.35/makaba/makaba.fcgi?json=1"
		####################################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.MAXTRIES = config.getint("BANS_CHECKER", "MAXTRIES")
		self.TIMEOUT = aiohttp.ClientTimeout(total=50, connect=config.getint("BANS_CHECKER", "TIMEOUT"))
		self.TASKS = config.getint("BANS_CHECKER", "TASKS")
		self.BOARD = config.get("BANS_CHECKER", "BOARD")
		self.PROXY = config.get("main", "PROXY")
		#####################################
		# список тредов
		self.ThreadList = []
		# живые без бана
		self.green = []
		# мертвые
		self.died = []
		# забаненные
		self.banned = []
		##################
		with open("texts/headers.json") as file:
			hds = json.loads(file.read())
			self.headers_2ch = hds["HEADERS_2CH"]
		##########################################
		with open("texts/usrAgents.txt") as file:
			self.agents = file.read().split("\n")
			while True:
				try:
					self.agents.remove("")
				except:
					break
		##########################################
		self.headers_2ch["Refer"] = f"https://2ch.hk/{self.BOARD}/"

	def get_board(self):
		'''Получение списка тредов'''
		print(self.NAME + "Получение списка тредов...")
		if self.PROXY != "0":
			proxies = {
			"https": self.PROXY,
			"http": self.PROXY
			}
		else:
			proxies = None
		#######################
		answ = None
		while True:
			try:
				req = backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries = 10, jitter = None, max_time = 30)(get)
				answ = json.loads(req(''.join(["https://2ch.hk/" + self.BOARD + "/catalog.json"]), verify=False, headers=self.headers_2ch, timeout=30, proxies=proxies).text)
			except Exception as e:
				print(self.NAME + 'Ошибка загрузки тредов!')
				input(self.NAME + "Проверьте подключение к интернету и нажмите любую клавишу...")
				continue
			else:
				print(self.NAME + 'Треды загружены успешно!')
				break
		return self.list_of_posts(answ)

	@staticmethod
	def list_of_posts(answer):
		'''
		Обработка каталога и получения номеров треда
		'''
		lst = []
		for i in range(0, len(answer)):
			lst.append(answer['threads'][i]['num'])
		return lst

	async def sendWithProxy(self, proxy, params, **kwargs):
		'''
		Отправка запроса с прокси
		'''
		async with aiohttp.ClientSession(connector=ProxyConnector.from_url(f'{self.protocol}://{proxy}'), **kwargs,) as session:
			async with session.post(self.url, ssl=False, params=params) as response:
				return await response.json()

	def answerStatus(self, response):
		'''
		Анализ ответа на [данные удалены]
		'''
		if response["message"] == 'Тред не существует.':
			return False
		elif response['message'] == '':
			return True
		else:
			print(self.NAME + coloring(f"Нестандартный ответ: {str(response)}", "red"))
			return False

	async def banChecker(self):
		'''
		Асинхронная задача для проверки на баны
		'''
		send = backoff.on_exception(backoff.expo, Exception, max_time=120, max_tries=self.MAXTRIES, jitter=None)(self.sendWithProxy)
		while True:
			async with self.lock:
				if len(self.proxies):
					proxy = self.proxies.pop()
				else:
					break
			##########################################
			thread = self.ThreadList[random.randint(0, len(self.ThreadList)-1)]
			params = {
						'task': 'report',
						'board': self.BOARD,
						'thread': thread,
						'comment': ''.join(str(random.randint(100000, 10000000))),
						'posts': thread
						}
			headers = copy.deepcopy(self.headers_2ch)
			headers["User-Agent"] = self.agents[random.randint(0, len(self.agents)-1)]
			##########################################
			try:
				response = await send(proxy, params, timeout=self.TIMEOUT, headers=headers)
			except KeyboardInterrupt:
				break
			except Exception as e:
				async with self.lock:
					self.died.append(proxy)
				print(self.NAME + coloring(f"[{str(len(self.proxies))}]Нерабочий прокси: {proxy}", "white"))
			else:
				###############################
				if self.answerStatus(response):
					async with self.lock:
						self.green.append(proxy)
					print(self.NAME + coloring(f"[{str(len(self.proxies))}]Найден рабочий прокси: {proxy}", "green"))
				###############################
				else:
					async with self.lock:
						self.banned.append(proxy)
					print(self.NAME + coloring(f"[{str(len(self.proxies))}]Найден забаненный прокси: {proxy}", "red"))

	@tools.errorsCap
	def main(self):
		'''
		Собственно, сам запуск
		'''
		print(self.NAME + coloring("Проверка на баны началась...", "green"))
		##################################
		self.lock = asyncio.Lock()
		self.ThreadList = self.get_board()
		loop = asyncio.get_event_loop()
		ignore_aiohttp_ssl_eror(loop)
		tasks = []
		##############################
		for i in range(0, self.TASKS):
			tasks.append(loop.create_task(self.banChecker()))
		###########################################################################
		try:
			loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except KeyboardInterrupt:
			print("\n" + self.NAME + coloring("Проверка отменена! Завершение задач...", "yellow"))
			for i in tasks:
				i.cancel()
		except Exception as e:
			raise e
		else:
			tools.loopResponse(loop_response, "bans checker")
		#######################################################################
		with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
			for i in self.died:
				file.write(i + "\n")
		#########################################################################
		with open("trashproxies/banned.txt", mode="a", encoding="UTF-8") as file:
			for i in self.banned:
				file.write(i + "\n")
		##########################################################
		print(self.NAME + coloring(f"Записаны нерабочие прокси в trashproxies/died.txt {str(len(self.died))} единиц.", "green"))
		print(self.NAME + coloring(f"Записаны забаненные прокси в trashproxies/banned.txt {str(len(self.banned))} единиц.", "green"))
		print(self.NAME + coloring("Проверка на баны закончилась...", "green"))
		return self.green



if __name__ == '__main__':
	pass