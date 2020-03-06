# -*- coding: utf-8 -*-



import asyncio
import aiohttp
import configparser
import colorama
colorama.init(autoreset=True)
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
from modules import tools


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
	Parser class
	'''
	def __init__(self, settings, *args):
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
		self.MAINURLS = ( # sites for parsing
			"http://www.proxyserverlist24.top/",
			"http://www.socks24.org",
			"http://www.vipsocks24.net/",
			"http://www.socksproxylist24.top/",
			"http://www.sslproxies24.top/",
			*args
			)
		self.MAINURLS = set(self.MAINURLS)
		####################################
		config = configparser.ConfigParser()
		config.read(settings, encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.TIMEOUT = aiohttp.ClientTimeout(total=30, connect=config.getint("PARSER", "TIMEOUT"))
		self.MAXTRIES = config.getint("PARSER", "MAXTRIES")
		self.TASKS = config.getint("PARSER", "TASKS")


	def main(self):
		'''
		Start function for start parser object
		'''
		print(self.NAME + colorama.Fore.GREEN + "Started parse...")
		##############################################
		self.inputLinks = copy.deepcopy(self.MAINURLS)
		self.lock = asyncio.Lock()
		loop = asyncio.get_event_loop()
		tasks = []
		ignore_aiohttp_ssl_eror(loop)
		#############################
		for i in range(0, 3):
			##############################
			for i in range(0, self.TASKS):
				tasks.append(loop.create_task(self.getWebPage()))
			####
			try:
				loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
			except Exception as e:
				if isinstance(e, (KeyboardInterrupt, RuntimeError, AttributeError)):
					print("\n" + self.NAME + colorama.Fore.YELLOW + "Parsing stopped! Cancelling all tasks...")
					for i in tasks:
						i.cancel()
					break
				else:
					raise e
			finally:
				self.inputLinks.clear()
				self.inputLinks = copy.deepcopy(self.links)
				self.links.clear()
		#########################################
			for i in self.links:
				if "zip" in i:
					self.zipLinks.add(i)
				else:
					self.inputLinks.add(i)
		#########################################
		print(self.NAME + colorama.Fore.GREEN + "Analyze founded URLs...")
		self.inputLinks = copy.deepcopy(self.zipLinks)
		##############################################
		for i in range(0, self.TASKS):
				tasks.append(loop.create_task(self.getWebPage()))
		#########################################################
		try:
			loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except Exception as e:
			if isinstance(e, (KeyboardInterrupt, RuntimeError, AttributeError)):
				print("\n" + self.NAME + colorama.Fore.YELLOW + "Parsing stopped! Cancelling all tasks...")
				for i in tasks:
					i.cancel()
			else:
				raise e
		else:
			tools.loopResponse(loop_response, "parser archives")
		#############################################################
		# downloading archives
		self.inputLinks = copy.deepcopy(self.linksForDownload)
		print(self.NAME + colorama.Fore.GREEN + "Downloading .zip archives...")
		#############################################################
		for i in range(0, self.TASKS):
				tasks.append(loop.create_task(self.DownloadArchive()))
		#############################################################
		try:
			loop_response = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
		except Exception as e:
			if isinstance(e, (KeyboardInterrupt, RuntimeError, AttributeError)):
				print("\n" + self.NAME + colorama.Fore.YELLOW + "Parsing stopped! Cancelling all tasks...")
				for i in tasks:
					i.cancel()
			else:
				raise e
		else:
			tools.loopResponse(loop_response, "download archives")
		###################################################
		try:
			self.zipExtractor()
		except Exception as e:
			if "downloads" in os.getcwd():
				os.chdir("..")
			if os.access("downloads", mode=0):
				rmtree("downloads")
			tools.log(e, "open archives")
		#################################################################
		print(self.NAME + colorama.Fore.GREEN + "Finished parsing proxies.")
		print(self.NAME + f"Got {str(len(self.proxies))} proxies.")
		self.proxies = [*self.proxies]
		#################################################################
		return self.proxies

	@staticmethod
	def getLinks(response):
			'''
			Parsing links from html
			'''
			answer = bs4.BeautifulSoup(response, "lxml")
			answer = answer.find_all("a")
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
		Gettings donwload links
		'''
		answer = bs4.BeautifulSoup(response, "lxml")
		answer = answer.find_all("a")
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
		async with aiohttp.ClientSession(**kwargs) as session:
			async with session.get(url, ssl=False) as response:
				return await response.text()

	@staticmethod
	async def download(url, **kwargs):
		'''
		Downloading file
		'''
		async with aiohttp.ClientSession(**kwargs) as session:
			async with session.get(url, ssl=False, allow_redirects=True) as response:
				return await response.read()

	async def getWebPage(self):
		'''
		Async function for searching proxies on sites
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
				response = await send(i, timeout=self.TIMEOUT, headers=headers)
			except KeyboardInterrupt:
				break
			except Exception as e:
				print(self.NAME + f"[{str(len(self.inputLinks))}]Failed to get web-page: {i}")
			else:
				local_links = self.getLinks(response)
				self.parseProxies(response)
				###############
				async with self.lock:
					self.links.update(local_links)
					self.getDownloadLinks(response)
				###################################
				print(self.NAME + colorama.Fore.GREEN + f"[{str(len(self.inputLinks))}]Successfully parsed page: {i}")

	async def DownloadArchive(self):
		'''
		Downloading archives and extracting
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
				print(self.NAME + f"Failed to download archive {i}")
			else:
				self.saveArchive(response)

	def zipExtractor(self):
		'''
		Extracting zip files
		'''
		os.chdir("downloads")
		files = os.listdir()
		########################
		for i in files:
			###################
			if not ".zip" in i:
				os.chmod(i, 0o777)
				os.remove(i)
				continue
			###################
			try:
				xfile = zipfile.ZipFile(i)
				xfile.extractall()
				xfile.close()
			except Exception as e:
				os.remove(i)
				print(self.NAME + colorama.Fore.RED + f"Error while extracting archive {i}")
				#raise e
				continue
			else:
				print(self.NAME + colorama.Fore.GREEN + f"Successfully extracted archive {i}")
			##################
			# list of extracted files
			extracted = os.listdir()
			##################
			for l in extracted:
				# parsing proxies from txt files
				if ".txt" in l:
					self.loadProxies_(l)
			##################
			# removing shit
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
						print(self.NAME + colorama.Fore.RED + f"Error {e} while deleting file {j}")
						tools.log(e, "zipExtractor")
			#################
			os.remove(i)
			#################
		os.chdir("..")
		try:
			os.rmdir("downloads")
		except OSError:
			rmtree("downloads")
		except Exception as e:
			tools.log(e, "remove downloads")

	def parseProxies(self, string):
		'''
		Parsing proxies with RegEx
		'''
		if not isinstance(string, str):
			string = str(string)
		proxies_find = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", string)
		self.proxies.update(proxies_find)

	def saveArchive(self, content):
		'''
		Saving archive
		'''
		filename = os.getcwd() + "/downloads/" + str(random.randint(1, 10000)) + ".zip"
		with open(filename, mode="wb") as file:
			file.write(content)
		os.chmod(filename, 0o777)
		print(self.NAME + colorama.Fore.GREEN + f"Successfully downloaded archive {filename}")

	def loadProxies_(self, txt):
		'''
		Opening txt files
		'''
		with open(txt, mode="r") as file:
			proxies = file.read().split("\n")
			while True:
				try:
					proxies.remove("")
				except:
					break
		print(self.NAME + colorama.Fore.GREEN +  f"Got {str(len(proxies))} proxies.")
		self.proxies.update(proxies)



if __name__ == '__main__':
	pass