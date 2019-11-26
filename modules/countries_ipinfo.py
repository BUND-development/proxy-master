# -*- coding: utf-8 -*-


import asyncio
import aiohttp
import backoff
import configparser
import json
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)
import colorama
colorama.init()
from modules import coloring, logwrite, tools
coloring = coloring.coloring
import ssl
import aiohttp_proxy
from aiohttp_proxy import ProxyConnector


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



class CheckerIpinfo(object):
	"""Проверка на ASN-номера провайдеров"""
	def __init__(self, proxies, protocol):
		super().__init__()
		self.proxies = proxies
		self.protocol = protocol
		###################################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.TIMEOUT = aiohttp.ClientTimeout(total=40, connect=config.getint("COUNTRIES_ADVANCED", "TIMEOUT"))
		self.MAXTRIES = config.getint("COUNTRIES_ADVANCED", "MAXTRIES")
		self.TASKS = config.getint("COUNTRIES_ADVANCED", "TASKS")
		self.UNKNOWN = config.getboolean("COUNTRIES_ADVANCED", "UNKNOWN")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		#####################################
		with open("texts/ASN.txt", mode="r") as file:
			self.ASN = file.read().split()
			while True:
				try:
					self.ASN.remove("")
				except:
					break
			print(self.NAME + "ASN-номера загружены успешно!")
		##################
		self.green = []
		self.died = []
		self.bad = []

	@tools.errorsCap
	def main(self):
		'''
		ipinfo checker main
		'''
		print(self.NAME + coloring("Началась проверка на ASN-номера через ipinfo...", "green"))
		##################################
		self.lock = asyncio.Lock()
		loop = asyncio.get_event_loop()
		ignore_aiohttp_ssl_eror(loop)
		tasks = []
		##############################
		for i in range(0, self.TASKS):
			tasks.append(loop.create_task(self.asnChecker()))
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
			tools.loopResponse(loop_response, "ipinfo")
		#######################################################################
		with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
			for i in self.died:
				file.write(i + "\n")
		#########################################################################
		with open("trashproxies/badASN.txt", mode="a", encoding="UTF-8") as file:
			for i in self.bad:
				file.write(i + "\n")
		##########################################################
		print(self.NAME + coloring(f"Записаны нерабочие прокси в trashproxies/died.txt {str(len(self.died))} единиц.", "green"))
		print(self.NAME + coloring(f"Записаны прокси с ASN из блек-листа в trashproxies/badASN.txt {str(len(self.bad))} единиц.", "green"))
		print(self.NAME + coloring("Проверка ASN закончилась.", "green"))
		return self.green

	async def asnChecker(self):
		'''
		Асинхронная функция проверки на ASN
		'''
		send = backoff.on_exception(backoff.expo, Exception, max_time=120, max_tries=self.MAXTRIES, jitter=None)(self.sendWithProxy)
		#############
		while True:
			async with self.lock:
				try:
					proxy = self.proxies.pop()
				except:
					break
			#############
			try:
				answer = await send(proxy, timeout=self.TIMEOUT)
			except Exception as e:
				print(self.NAME + coloring(f"[{str(len(self.proxies))}]Нерабочая прокси {proxy}", "white"))
				async with self.lock:
					self.died.append(proxy)
			else:
				if self.getStatus(answer):
					print(self.NAME + coloring(f"[{str(len(self.proxies))}]Рабочая прокси {proxy}", "green"))
					async with self.lock:
						self.green.append(proxy)
				else:
					print(self.NAME + coloring(f"[{str(len(self.proxies))}]Прокси с запрещенным ASN {proxy}", "yellow"))
					async with self.lock:
						self.bad.append(proxy)

	async def sendWithProxy(self, proxy, **kwargs):
		'''
		Отправка запроса с прокси
		'''
		_ = proxy.split(":")[0]
		async with aiohttp.ClientSession(connector=ProxyConnector.from_url(f'{self.protocol}://{proxy}'), **kwargs,) as session:
			async with session.get(f"http://ipinfo.io/{_}/json", ssl=False) as response:
				return await response.json()

	def getStatus(self, answer):
		try:
			answer = answer["org"].split(" ")[0]
		except:
			if self.UNKNOWN:
				return True
			else:
				return False
		for i in self.ASN:
			if answer == i:
				break
			else:
				return True
			return False
		