# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import backoff
import configparser
import json
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)
import colorama
colorama.init(autoreset=True)
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



class Countries2Ip(object):
	'''
	Checking coutnries and countries code with 2ip.ru
	'''
	def __init__(self, proxies, settings):
		super().__init__()
		self.proxies = proxies
		self.TIMEOUT = aiohttp.ClientTimeout(total= 30, connect=10)
		self.green = []
		self.died = []
		self.bad = []
		self.time = 30
		#######################
		config = configparser.ConfigParser()
		config.read(settings, encoding="UTF-8")
		self.token = config["2IP"]["TOKEN"]
		self.TASKS = config.getint("2IP", "TASKS")
		self.unknown = config.getboolean("2IP", "UNKNOWNOUT")
		self.CHECK2IP = config.getboolean("modules", "CHECK2IP")
		self.CHECK2IP_CODES = config.getboolean("modules", "CHECK2IP_CODES")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		del config
		###################
		self.headers = {
		"X-API-Token": self.token,
		"User-Agent": "curl/7.64.0",
		}
		###########################################################
		with open("texts/countries.txt", encoding="UTF-8") as file:
			self.countries = file.read().split("\n")
			while True:
				try:
					self.countries.remove("")
				except:
					break
		#################################################################
		with open("texts/countriesCodes.txt", encoding="UTF-8") as file:
			self.countriesCodes = file.read().split("\n")
			while True:
				try:
					self.countriesCodes.remove("")
				except:
					break
	
	@tools.errorsCap
	def main(self):
		print(self.NAME + colorama.Fore.GREEN + "Started 2ip check...")
		##################################
		self.lock = asyncio.Lock()
		loop = asyncio.get_event_loop()
		ignore_aiohttp_ssl_eror(loop)
		tasks = []
		##############################
		for i in range(0, self.TASKS):
			tasks.append(loop.create_task(self.countriesChecker()))
		###########################################################################
		#self.event = asyncio.Event()
		#tasks.append(loop.create_task(tools.awaiter(self.time, self.event, self.NAME, self.proxies)))
		########
		try:
			loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except KeyboardInterrupt:
			print("\n" + self.NAME + colorama.Fore.YELLOW + "Check cancelled! Exiting...")
			for i in tasks:
				i.cancel()
		except Exception as e:
			raise e
		else:
			tools.loopResponse(loop_response, "2ip")
		#######################################################################
		# with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
		# 	for i in self.died:
		# 		file.write(i.normal + "\n")
		#########################################################################
		with open("trashproxies/fromBadCountries.txt", mode="a", encoding="UTF-8") as file:
			for i in self.bad:
				file.write(i.normal + "\n")
		##########################################################
		print(self.NAME + colorama.Fore.GREEN + f"Proxies from blacklist-countries trashproxies/fromBadCountries.txt, {len(self.bad)}")
		print(self.NAME + colorama.Fore.GREEN + "Check finished.")
		return self.green

	async def countriesChecker(self):
		send = backoff.on_exception(backoff.expo, Exception, max_time=90, max_tries=3, jitter=None)(self.send_)
		async with aiohttp.ClientSession(headers=self.headers, timeout=self.TIMEOUT) as session:
			###########
			while True:
				################
				# if self.event.is_set():
				# 	await asyncio.sleep(self.time)
				# 	continue
				#####################
				async with self.lock:
					try:
						i = self.proxies.pop()
					except IndexError:
						break
					except Exception as e:
						raise e
				#########
				try:
					answer = await send(i, session)
				except KeyboardInterrupt:
					break
				except Exception as e:
					async with self.lock:
						self.proxies.append(i)
					raise e
				else:
					if self.getCountriesStatus(answer):
						async with self.lock:
							self.green.append(i)
						print(self.NAME + colorama.Fore.GREEN + f"[{str(len(self.proxies))}]Good proxy: {i.normal}")
					else:
						async with self.lock:
							self.bad.append(i)
						print(self.NAME + colorama.Fore.YELLOW + f"[{str(len(self.proxies))}]Proxy from blacklist country: {i.normal}")

	@staticmethod
	async def send_(proxy, session):
		#async with aiohttp.ClientSession(headers=self.headers, **kwargs) as session:
		async with session.get("https://2ip.ru/api/v1.0/geo/" + proxy.host) as respone:
			return await respone.json()

	@tools.errorsCap
	def getCountriesStatus(self, response):
		##############################################################
		if response["info"] == 'Информации по данному ip не найдено':
			if self.unknown:
				return True
			else:
				return False
		####################
		if self.CHECK2IP:
			try:
				response = response["info"]["country"]
			except KeyError:
				if self.unknown:
					return True
				else:
					False
			except Exception as e:
				raise e
			else:
				for country in self.countries:
					if response == country:
						break
				else:
					return True
		#####################
		elif self.CHECK2IP_CODES:
			try:
				response = response["info"]["countryCode"]
			except KeyError:
				if self.unknown:
					return True
				else:
					return False
			except Exception as e:
				raise e
			else:
				for country in self.countriesCodes:
					if response == country:
						break
				else:
					return True
		return False



if __name__ == '__main__':
	pass