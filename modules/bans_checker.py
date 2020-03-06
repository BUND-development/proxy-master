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



class BoardGetError(exceptions.ConnectionError):
	pass



class BansChecker(object):
	'''
	Bans checker class
	'''
	def __init__(self, proxies, settings):
		super().__init__()
		self.proxies = proxies
		self.url = "http://2ch.hk/makaba/makaba.fcgi"
		####################################
		config = configparser.ConfigParser()
		config.read(settings, encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.MAXTRIES = config.getint("BANS_CHECKER", "MAXTRIES")
		self.TIMEOUT = aiohttp.ClientTimeout(total=50, connect=config.getint("BANS_CHECKER", "TIMEOUT"))
		self.TASKS = config.getint("BANS_CHECKER", "TASKS")
		self.BOARD = config.get("BANS_CHECKER", "BOARD")
		self.PROXY = config.get("main", "PROXY")
		#####################################
		self.ThreadList = []
		self.green = []
		self.died = []
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
		self.headers_2ch["Refer"] = f"http://2ch.hk/{self.BOARD}/"

	def get_board(self):
		'''Parsing thread numbers from 2ch.hk'''
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
				print(self.NAME + 'Failed to load 2ch threads!')
				input(self.NAME + "Check your connection and press any key...")
				continue
			else:
				print(self.NAME + 'Threads loaded successfully')
				break
		return self.list_of_posts(answ)

	@staticmethod
	def list_of_posts(answer):
		'''
		Parsing numbers of threads from response
		'''
		lst = []
		for i in range(0, len(answer)):
			lst.append(answer['threads'][i]['num'])
		return lst

	async def sendWithProxy(self, proxy, params, **kwargs):
		'''
		Sending request
		'''
		async with aiohttp.ClientSession(connector=ProxyConnector.from_url(proxy.formated), **kwargs,) as session:
			async with session.post(self.url, ssl=False, params=params) as response:
				return await response.text()

	def answerStatus(self, response):
		'''
		Returns result of ban check
		'''
		if "Тред не существует." in response:
			return False
		elif "OK" in response:
			return True
		elif "Плановые техработы" in response:
			time.sleep(30)
			print(self.NAME + colorama.Fore.RED + "Makaba is down.")
			return False
		else:
			print(self.NAME + colorama.Fore.YELLOW + f"Unknown unswer: {str(response)}")
			return False

	async def banChecker(self):
		'''
		Async task for checking bans
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
				print(self.NAME + f"[{str(len(self.proxies))}]Died proxy: {proxy.normal}")
			else:
				###############################
				if self.answerStatus(response):
					async with self.lock:
						self.green.append(proxy)
					print(self.NAME + colorama.Fore.GREEN + f"[{str(len(self.proxies))}]Good proxy: {proxy.normal}")
				###############################
				else:
					async with self.lock:
						self.banned.append(proxy)
					print(self.NAME + colorama.Fore.RED + f"[{str(len(self.proxies))}]Banned proxy: {proxy.normal}")

	#@tools.errorsCap
	def main(self):
		'''
		main of bans checker
		'''
		print(self.NAME + colorama.Fore.GREEN + "Started bans checker...")
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
			print("\n" + self.NAME + colorama.Fore.YELLOW + "Check cancelled! Exiting...")
			for i in tasks:
				i.cancel()
		except Exception as e:
			raise e
		else:
			tools.loopResponse(loop_response, "bans checker")
		#######################################################################
		with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
			for i in self.died:
				file.write(i.normal + "\n")
		#########################################################################
		with open("trashproxies/banned.txt", mode="a", encoding="UTF-8") as file:
			for i in self.banned:
				file.write(i.normal + "\n")
		##########################################################
		print(self.NAME + colorama.Fore.GREEN + f"Bad proxies in trashproxies/died.txt, {len(self.died)}")
		print(self.NAME + colorama.Fore.GREEN + f"Banned proxies in trashproxies/banned.txt, {len(self.banned)}")
		print(self.NAME + colorama.Fore.GREEN + "Bans check finished!")
		return self.green



if __name__ == '__main__':
	pass