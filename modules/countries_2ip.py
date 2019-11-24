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
	Проверка на страны и коды стран через 2ip.ru
	'''
	def __init__(self, proxies):
		super().__init__()
		self.proxies = proxies
		self.TIMEOUT = aiohttp.ClientTimeout(total= 30, connect=10)
		self.green = []
		self.died = []
		self.bad = []
		#######################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
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
		print(self.NAME + coloring("Началась проверка на страны через 2ip.ru...", "green"))
		##################################
		self.lock = asyncio.Lock()
		loop = asyncio.get_event_loop()
		ignore_aiohttp_ssl_eror(loop)
		tasks = []
		##############################
		for i in range(0, self.TASKS):
			tasks.append(loop.create_task(self.countriesChecker()))
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
			tools.loopResponse(loop_response, "2ip")
		#######################################################################
		with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
			for i in self.died:
				file.write(i + "\n")
		#########################################################################
		with open("trashproxies/fromBadCountries.txt", mode="a", encoding="UTF-8") as file:
			for i in self.bad:
				file.write(i + "\n")
		##########################################################
		print(self.NAME + coloring(f"Записаны нерабочие прокси в trashproxies/died.txt {str(len(self.died))} единиц.", "green"))
		print(self.NAME + coloring(f"Записаны прокси из заблокированных стран в trashproxies/fromBadCountries.txt {str(len(self.bad))} единиц.", "green"))
		print(self.NAME + coloring("Проверка стран закончилась.", "green"))
		return self.green

	async def countriesChecker(self):
		send = backoff.on_exception(backoff.expo, Exception, max_time=90, max_tries=3, jitter=None)(self.send_)
		async with aiohttp.ClientSession(headers=self.headers, timeout=self.TIMEOUT) as session:
			###########
			while True:
				################
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
						self.died.append(i)
					print(self.NAME + coloring(f"[{str(len(self.proxies))}]Нерабочий прокси: {i}", "white"))
				else:
					if self.getCountriesStatus(answer):
						async with self.lock:
							self.green.append(i)
						print(self.NAME + coloring(f"[{str(len(self.proxies))}]Незаблокированный прокси: {i}", "green"))
					else:
						async with self.lock:
							self.bad.append(i)
						print(self.NAME + coloring(f"[{str(len(self.proxies))}]Прокси из заблокированной страны: {i}", "yellow"))

	@staticmethod
	async def send_(proxy, session):
		#async with aiohttp.ClientSession(headers=self.headers, **kwargs) as session:
		async with session.get("https://2ip.ru/api/v1.0/geo/" + proxy.split(":")[0]) as respone:
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