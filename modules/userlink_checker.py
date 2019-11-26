# -*- coding: utf-8 -*-


import asyncio
import aiohttp
import aiohttp_proxy
import json
import configparser
import colorama
colorama.init()
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)
from modules import coloring
coloring = coloring.coloring
from modules import logwrite
import backoff
from aiohttp_proxy import ProxyConnector
import copy
import random
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



class UnsupportedType(TypeError):
	pass



class UserChecker(object):
	'''
	Юзер-чекер
	'''
	def __init__(self, proxies, protocol):
		super().__init__()
		self.proxies = proxies
		self.protocol = protocol
		self.died = []
		self.green = []
		self.bad = []
		############################################
		with open("texts/userParams.json") as file:
			jsonLoads = json.loads(file.read())
			self.params = jsonLoads["params"]
			self.data = jsonLoads["data"]
		############################################
		with open("texts/headers.json") as file:
			hds = json.loads(file.read())
			self.headers = hds["HEADERS_CUSTOM"]
		############################################
		with open("texts/usrAgents.txt") as file:
			self.agents = file.read().split("\n")
			while True:
				try:
					self.agents.remove("")
				except:
					break
		#####################################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.TIMEOUT = aiohttp.ClientTimeout(total=40, connect=config.getint("USER_CHECKER", "TIMEOUT"))
		self.MAXTRIES = config.getint("USER_CHECKER", "MAXTRIES")
		self.TASKS = config.getint("USER_CHECKER", "TASKS")
		self.PARAMS = config.getboolean("USER_CHECKER", "PARAMS")
		self.DATA = config.getboolean("USER_CHECKER", "DATA")
		self.URL = config.get("USER_CHECKER", "URL")
		self.TYPE = config.get("USER_CHECKER", "REQUEST")

	def checkingData(self):
		'''
		Проверка запрашиваемого типа запроса
		'''
		if self.TYPE in "GET POST HEAD":
			pass
		else:
			raise UnsupportedType(f"Неподдерживаемый тип запроса {self.TYPE}")

	def main(self):
		print(self.NAME + coloring("Проверка юзер-запросами началась...", "green"))
		###################
		self.checkingData()
		self.lock = asyncio.Lock()
		loop = asyncio.get_event_loop()
		tasks = []
		ignore_aiohttp_ssl_eror(loop)
		#############################
		for i in range(0, self.TASKS):
			tasks.append(loop.create_task(self.startingCheck()))
		#############
		try:
			loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except KeyboardInterrupt:
			print("\n" + self.NAME + coloring("Проверка отменена!", "yellow"))
			for i in tasks:
				i.cancel()
		except UnsupportedType:
			print(self.NAME + coloring(f"Неподдерживаемый тип запроса {self.TYPE}", "red"))
		except Exception as e:
			raise e
		########################
		with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
			for i in self.died:
				file.write(i + "\n")
		#########################
		with open("trashproxies/userBad.txt", mode="a", encoding="UTF-8") as file:
			for i in self.bad:
				file.write(i + "\n")
		###########################
		print(self.NAME + coloring(f"Записаны нерабочие прокси в trashproxies/died.txt {str(len(self.died))} единиц.", "green"))
		print(self.NAME + coloring(f"Записаны заблокированные прокси в trashproxies/userBad.txt {str(len(self.bad))} единиц.", "green"))
		print(self.NAME + coloring("Проверка юзер-запросами закончилась...", "green"))
		return self.green

	async def sendWithProxy(self, proxy, requestKwargs, **kwargs):
		'''
		Отправка запроса
		'''
		async with aiohttp.ClientSession(connector=ProxyConnector.from_url(f'{self.protocol}://{proxy}'), **kwargs,) as session:
			if self.TYPE == "POST":
				async with session.post(self.URL, ssl=False, **requestKwargs) as response:
					return await response.text()
			elif self.TYPE == "GET":
				async with session.get(self.URL, ssl=False, **requestKwargs) as response:
					return await response.text()
			elif self.TYPE == "HEAD":
				async with session.head(self.URL, ssl=False, **requestKwargs) as response:
					return await response.text()
			else:
				raise UnsupportedType("Неподдерживаемый тип запроса!")

	async def userFilter(self, response):
		'''
		Юзер фильтр, замописный. Принимает ответный текст запроса. Если ответ 
		правильный/нужный - возвращает True, иначе false. Пример ниже.
		'''
		# if my_value in response:
		# 	return True
		# else:
		# 	return False
		#
		return True

	async def startingCheck(self):
		send = backoff.on_exception(backoff.expo, Exception, max_time=60, max_tries=self.MAXTRIES, jitter=None)(self.sendWithProxy)
		##############
		while True:
			################
			async with self.lock:
				if len(self.proxies):
					proxy = self.proxies.pop()
				else:
					break
			kwargs = {}
			if self.PARAMS:
				kwargs["params"] = self.params
			if self.DATA:
				kwargs["data"] = self.data
			headers = copy.deepcopy(self.headers)
			headers["User-Agent"] = self.agents[random.randint(0, len(self.agents)-1)]
			#################
			try:
				response = await send(proxy, kwargs, timeout=self.TIMEOUT, headers=headers)
			except UnsupportedType:
				raise UnsupportedType
				break
			except KeyboardInterrupt:
				for i in asyncio.all_tasks():
					i.cancel()
				loop = asyncio.get_running_loop()
				loop.stop()
				break
			except Exception as e:
				#print(e)
				async with self.lock:
					self.died.append(proxy)
				print(self.NAME + coloring(f"[{str(len(self.proxies))}]Нерабочий прокси: {proxy}", "white"))
			else:
				if await self.userFilter(response):
					async with self.lock:
						self.green.append(proxy)
					print(self.NAME + coloring(f"[{str(len(self.proxies))}]Найден рабочий прокси: {proxy}", "green"))
				else:
					async with self.lock:
						self.bad.append(proxy)
					print(self.NAME + coloring(f"[{str(len(self.proxies))}]Найден заблокированный прокси: {proxy}", "yellow"))



if __name__ == '__main__':
	pass