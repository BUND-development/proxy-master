# -*- coding: utf-8 -*-


import asyncio
import backoff
import configparser
import json
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)
import colorama
colorama.init(autoreset=True)
from modules import tools
import ssl
import aiohttp_proxy
from aiohttp_proxy import ProxyConnector
import aiohttp



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
	"""Checking ASN of provider"""
	def __init__(self, proxies, settings):
		super().__init__()
		self.proxies = proxies
		self.time = 60
		###################################
		config = configparser.ConfigParser()
		config.read(settings, encoding="UTF-8")
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
		##################
		self.green = []
		self.died = []
		self.bad = []

	#@tools.errorsCap
	def main(self):
		'''
		ipinfo checker main
		'''
		print(self.NAME + colorama.Fore.GREEN + "Starting ASN check...")
		##################################
		self.lock = asyncio.Lock()
		loop = asyncio.get_event_loop()
		ignore_aiohttp_ssl_eror(loop)
		tasks = []
		##############################
		for i in range(0, self.TASKS):
			tasks.append(loop.create_task(self.asnChecker()))
		########################################################
		#self.event = asyncio.Event()
		#tasks.append(loop.create_task(tools.awaiter(self.time, self.event, self.NAME, self.proxies)))
		###########################################################################
		try:
			loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except KeyboardInterrupt:
			print("\n" + self.NAME + colorama.Fore.YELLOW + "Check cancelled! Exiting...")
			for i in tasks:
				i.cancel()
		except Exception as e:
			raise e
		else:
			tools.loopResponse(loop_response, "ipinfo")
		#######################################################################
		with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
			for i in self.died:
				file.write(i.normal + "\n")
		#########################################################################
		with open("trashproxies/badASN.txt", mode="a", encoding="UTF-8") as file:
			for i in self.bad:
				file.write(i.normal + "\n")
		##########################################################
		print(self.NAME + colorama.Fore.GREEN + f"Bad proxies in trashproxies/died.txt, {len(self.died)}")
		print(self.NAME + colorama.Fore.GREEN + f"Proxy with blacklist ASN in trashproxies/badASN.txt, {len(self.died)}")
		print(self.NAME + colorama.Fore.GREEN + "ASN check finished!")
		return self.green

	async def asnChecker(self):
		'''
		Async task for checking ASN
		'''
		send = backoff.on_exception(backoff.expo, Exception, max_time=120, max_tries=self.MAXTRIES, jitter=None)(self.sendWithProxy)
		#############
		while True:
			# if self.event.is_set():
			# 		await asyncio.sleep(self.time)
			# 		continue
			####################
			async with self.lock:
				try:
					proxy = self.proxies.pop()
				except:
					break
			#############
			try:
				answer = await send(proxy, timeout=self.TIMEOUT)
			except Exception as e:
				async with self.lock:
					self.died.append(proxy)
				print(self.NAME + f"[{str(len(self.proxies))}]Died proxy: {proxy.normal}")
			else:
				if self.getStatus(answer):
					async with self.lock:
						self.green.append(proxy)
					print(self.NAME + colorama.Fore.GREEN + f"[{str(len(self.proxies))}]Good proxy: {proxy.normal}")
				else:
					async with self.lock:
						self.bad.append(proxy)
					print(self.NAME + colorama.Fore.YELLOW + f"[{str(len(self.proxies))}]Proxy with blacklist ASN: {proxy.normal}")

	async def sendWithProxy(self, proxy, **kwargs):
		'''
		Sending request from proxy
		'''
		async with aiohttp.ClientSession(connector=ProxyConnector.from_url(proxy.formated), **kwargs,) as session:
			async with session.get(f"http://ipinfo.io/{proxy.host}/json", ssl=False) as response:
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



if __name__ == '__main__':
	pass
		