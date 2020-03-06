# -*- coding: utf-8 -*-

import asyncio
import argparse
import os
import re

def errorsCap(func):
	if asyncio.iscoroutine(func):
		async def wrapper(*args, **kwargs):
			try:
				result = await func(*args, **kwargs)
			except Exception as e:
				log(e, func.__doc__)
			else:
				return result
	else:
		def wrapper(*args, **kwargs):
			try:
				result = func(*args, **kwargs)
			except Exception as e:
				log(e, func.__doc__)
			else:
				return result
	return wrapper



def loopResponse(response, name):
	for i in response:
		if i != None:
			log(i, name)



def log(error, module, **kwargs):
	with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
		params ="\n"
		try:
			st = open("settings.ini", encoding="UTF-8")
			settings = st.read()
		except:
			settings = "ERROR .ini"
		else:
			st.close()
		for key in kwargs:
			params = params + "\n" + str(key) + ":" + str(kwargs[key])
		text_log = "\n============\nmodule: {0}\nerror:{1}\n--another params--{2}\n settings: {3}\n============\n".format(module, error, params, settings)
		file.write(text_log)



def out_logo():
	print(r"  _____    _____     ____   __   __ __     __      __  __               _____   _______   ______   _____   ")
	print(r" |  __ \  |  __ \   / __ \  \ \ / / \ \   / /     |  \/  |     /\      / ____| |__   __| |  ____| |  __ \  ")
	print(r" | |__) | | |__) | | |  | |  \ V /   \ \_/ /      | \  / |    /  \    | (___      | |    | |__    | |__) | ")
	print(r" |  ___/  |  _  /  | |  | |   > <     \   /       | |\/| |   / /\ \    \___ \     | |    |  __|   |  _  /  ")
	print(r" | |      | | \ \  | |__| |  / . \     | |        | |  | |  / ____ \   ____) |    | |    | |____  | | \ \  ")
	print(r" |_|      |_|  \_\  \____/  /_/ \_\    |_|        |_|  |_| /_/    \_\ |_____/     |_|    |______| |_|  \_\ ", end="\n\n")
	print(r"  __       _____ ")
	print(r" /_ |     | ____|")
	print(r"  | |     | |__  ")
	print(r"  | |     |___ \ ")
	print(r"  | |  _   ___) |")
	print(r"  |_| (_) |____/ ", end="\n\n\n\n\n")



def cls():
	'''Clear terminal/console'''
	os.system('cls' if os.name=='nt' else 'clear') 



async def awaiter(time, event, name, proxies):
	while True:
		await asyncio.sleep(50)
		event.set()
		print(name + "To many requests, awaiting...")
		await asyncio.sleep(time*4)
		event.clear()
		if not len(proxies):
			return None




def libInstaller():
	try:
		if os.name=="nt":
			os.system("pip install --user requests pysocks urllib3 bs4 colorama \
				lxml pygeoip backoff termcolor configparser brotlipy aiohttp aiohttp_proxy progressbar")
		else:
			os.system("pip3 install --user requests pysocks urllib3 bs4 colorama \
				lxml pygeoip backoff termcolor configparser brotlipy aiohttp aiohttp_proxy progressbar")
	except:
		pass
	finally:
		exit(0)

class ProxyInitError(Exception):
	pass

class Proxy(object):
	''' special proxy object class '''
	def __init__(self, proxy, protocol="socks4", ignoreFormated=False):
		super().__init__()
		if re.match(r"^.{4,6}:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}.+", proxy) or re.match(r"^.{4,6}:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", proxy):
			proxy = proxy.split("://")
			if ignoreFormated:
				self.protocol = protocol
			else:
				self.protocol = proxy[0]
			proxy = proxy[1]
		elif re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}.+", proxy) or re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", proxy):
			self.protocol = protocol
		else:
			raise ProxyInitError("Failed to init proxy")

		proxy = proxy.split(":")
		# host:port:username:password
		if len(proxy) > 4:
			raise ProxyInitError("Failed to init proxy")
		elif len(proxy) > 2:
			self.username = proxy[2]
			self.password = proxy[3]
		else:
			self.username = None
			self.password = None

		self.host = proxy[0]
		self.port = proxy[1]

		if self.username and self.password:
			self.formated = f"{self.protocol}://{self.host}:{self.port}:{self.username}:{self.password}"
		else:
			self.formated = f"{self.protocol}://{self.host}:{self.port}"
		self.normal = f"{self.host}:{self.port}"
		self.octets = self.host.split(".")

	def __str__(self):
		return self.formated

	def __repr__(self):
		return self.formated



if __name__ == '__main__':
	#testFunc(1)
	pass
