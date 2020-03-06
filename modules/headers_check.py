# -*- coding: utf-8 -*-


import asyncio
import aiohttp
import json
import configparser
import backoff
from aiohttp_proxy import ProxyConnector
import colorama
colorama.init(autoreset=True)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from modules import tools
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



class HeadersChecker(object):
	'''
	Headers checker
	'''
	def __init__(self, proxies, settings):
		super().__init__()
		self.bad = []
		self.died = []
		self.green = []
		self.url = "http://sode.su/request.php"
		self.myIP = None
		self.blackHeaders = (
			"Forwarded",
			"X-Forwarded-Host",
			"Via",
			"PROXY_CONNECTION"
		)
		###################################
		config = configparser.ConfigParser()
		config.read(settings, encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.TIMEOUT = aiohttp.ClientTimeout(total=40, connect=config.getint("HEADERS_CHECKER", "TIMEOUT"))
		self.MAXTRIES = config.getint("HEADERS_CHECKER", "MAXTRIES")
		self.TASKS = config.getint("HEADERS_CHECKER", "TASKS")
		########################################

	#@tools.errorsCap
	def main(self):
		'''
		main of headers checker.
		'''
		print(self.NAME + colorama.Fore.GREEN + "Checking headers...")
		###########################
		self.lock = asyncio.Lock()
		loop = asyncio.get_event_loop()
		ignore_aiohttp_ssl_eror(loop)
		tasks = []
		###########################
		for i in range(0, self.TASKS):
			tasks.append(loop.create_task(self.headersChecker()))
		###########################
		try:
			loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except KeyboardInterrupt:
			print("\n" + self.NAME + colorama.Fore.YELLOW + "Check cancelled! Exiting...")
			for i in tasks:
				i.cancel()
		except Exception as e:
			raise e
		else:
			tools.loopResponse(loop_response, "headers")
		########################################################################
		print(self.NAME + colorama.Fore.GREEN + "Checking headers finished!")
		with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
			for i in self.died:
				file.write(i.normal + "\n")
		##########################################################################
		with open("trashproxies/nonAnon.txt", mode="a", encoding="UTF-8") as file:
			for i in self.bad:
				file.write(i.normal + "\n")
		####################################3
		print(self.NAME + colorama.Fore.GREEN + f"Bad proxies in trashproxies/died.txt, {len(self.died)}")
		print(self.NAME + colorama.Fore.GREEN + f"Proxy with blacklist ASN in trashproxies/nonAnon.txt, {len(self.bad)}")
		return self.green

	async def sendWithProxy(self, proxy, **kwargs):
		'''
		Отправка запроса с прокси
		'''
		async with aiohttp.ClientSession(connector=ProxyConnector.from_url(proxy.formated), **kwargs,) as session:
			async with session.post(self.url, ssl=False) as response:
				return await response.json()

	async def headersChecker(self, **kwargs):
		send = backoff.on_exception(backoff.expo, Exception, max_time=120, max_tries=self.MAXTRIES, jitter=None)(self.sendWithProxy)
		###########
		while True:
			###################
			async with self.lock:
				if len(self.proxies):
					proxy = self.proxies.pop()
				else:
					break
			####################
			try:
				response = await send(proxy, timeout=self.TIMEOUT)
			except KeyboardInterrupt:
				break
			except Exception as e:
				async with self.lock:
					self.died.append(proxy)
				print(self.NAME + f"[{str(len(self.proxies))}]Died proxy: {proxy.normal}")
			else:
				if await self.headersStatus(response, proxy):
					async with self.lock:
						self.green.append(proxy)
					print(self.NAME + colorama.Fore.GREEN + f"[{str(len(self.proxies))}]Good proxy: {proxy.normal}")
				else:
					async with self.lock:
						self.bad.append(proxy)
					print(self.NAME + colorama.Fore.RED + f"[{str(len(self.proxies))}]Bad-headers proxy: {proxy.normal}")

	async def headersStatus(self, headers, proxy):
		'''
		Анализ заголовков
		'''
		ip = headers["ip"]
		headers = headers["headers"]
		if headers["X-Forwarded-For"] != ip:
			return False
		################
		for i in self.blackHeaders:
			if headers.get(i) != None:
				break
		else:
			return True
		return False



if __name__ == '__main__':
	pass