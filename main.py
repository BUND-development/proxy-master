#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import os
import configparser
from modules import tools


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
	'''Очистка консоли'''
	os.system('cls' if os.name=='nt' else 'clear')



def decor(func):
	'''Используется для дебага'''
	import time
	def wrapper(*args, **kwargs):
		start = time.time()
		result = func(*args, **kwargs)
		end = time.time()
		print(end-start)
		return result
	return wrapper



def libInstaller():
	try:
		if os.name=="nt":
			os.system("pip install --user requests pysocks urllib3 bs4 colorama \
				lxml pygeoip backoff termcolor configparser brotlipy aiohttp aiohttp_proxy")
		else:
			os.system("pip3 install --user requests pysocks urllib3 bs4 colorama \
				lxml pygeoip backoff termcolor configparser brotlipy aiohttp aiohttp_proxy")
	except:
		pass
	finally:
		cls()



class Main():
	
	def __init__(self, *args, **kwargs):
		super().__init__()
		out_logo()
		self.export = []  # прокси на выход
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.PARSE = config.getboolean("modules", "PARSE")
		self.SUBNETS = config.getboolean("modules", "SUBNETS")
		self.BLACKLIST = config.getboolean("modules", "BLACKLIST")
		self.USER_CHECK = config.getboolean("modules", "USER_CHECK")
		self.CHECKON2CH = config.getboolean("modules", "CHECKON2CH")
		self.CHECK_ADVANCED = config.getboolean("modules", "CHECK_ADVANCED")
		self.SAME_FILTERING = config.getboolean("modules", "SAME_FILTERING")
		self.CHECK2IP = config.getboolean("modules", "CHECK2IP")
		self.COUNTRIES = config.getboolean("modules", "COUNTRIES")
		self.CHECK2IP_CODES = config.getboolean("modules", "CHECK2IP_CODES")
		self.CHECK_HEADERS = config.getboolean("modules", "CHECK_HEADERS")
		self.PROTOCOLOUT = config.getboolean("main", "PROTOCOLOUT")
		self.FILENAME_EXPORT = config["main"]["FILENAME_EXPORT"]
		self.NORMALINPUT = config.getboolean("main", "NORMALINPUT")
		self.FILTERINGBAD = config.getboolean("main", "FILTERINGBAD")
		self.NAME = "\x1b[32m" +  config["main"]["NAME"] + "\x1b[0m"
		del config
	
	@tools.errorsCap
	def main(self):
		'''
		main прокси-мастера
		'''
		self.geting()
		print(self.NAME + coloring("Ввод получен!", "green"))
		with open("input-proxies.txt", mode="r", encoding="UTF-8") as file:
			self.export = file.read().split("\n")
			while True:
				try:
					self.export.remove("")
				except:
					break

		if self.PARSE:
			start = proxy_parser.Parser()
			self.export = [*start.main()]
			self.export.extend(proxyscrape.start())

		if self.FILTERINGBAD:
			filtering = removeshit.Main(self.export, self.SAME_FILTERING)
			self.export = filtering.start()
		
		if self.BLACKLIST:
			filtering = blocked.Blocked(self.export)
			self.export = filtering.start()

		if self.SUBNETS:
			filtering = subnets_socket.FilteringSubnets(self.export)
			self.export = filtering.start()

		if self.CHECK2IP or self.CHECK2IP_CODES:
			filtering = countries_2ip.Countries2Ip(self.export)
			self.export = filtering.main()

		if self.COUNTRIES:
			self.export = weed.weed(self.export)

		if self.CHECK_ADVANCED:
			filtering = countries_ipinfo.CheckerIpinfo(self.export, self.TYPE)
			self.export = filtering.main()

		if self.CHECKON2CH:
			start = bans_checker.BansChecker(self.export, self.TYPE)
			self.export = start.main()

		if self.CHECK_HEADERS:
			start = headers_check.HeadersChecker(self.export, self.TYPE)
			self.export = start.main()

		if self.USER_CHECK:
			start = userlink_checker.UserChecker(self.export, self.TYPE)
			self.export = start.main()

		with open(self.FILENAME_EXPORT, mode="w", encoding="UTF-8") as file:
			print("", end="\n\n")
			try:
				self.export.remove("")
			except:
				pass
			print(self.NAME + "Всего {0} прокси-серверов.".format(str(len(self.export))))
			for i in self.export:
				if self.PROTOCOLOUT:
					file.write(self.TYPE + "://" + str(i) + "\n")
				else:
					file.write(str(i) + "\n")

	def geting(self):
		if self.NORMALINPUT:
			try:
				self.TYPE = sys.argv[1]
			except IndexError:
				print(self.NAME + coloring("Ты забыл написать параметр командной строки!", "red"))
				exit(1)
			if (sys.argv[1] != "http") and (sys.argv[1] != "https") and (sys.argv[1] != "socks4") and (sys.argv[1] != "socks5"):
				print(self.NAME + coloring("Введенный протокол прокси не поддерживается, ты точно ввел его правильно?", "red"))
				exit(1)
		else:
			self.TYPE = input(self.NAME + "Введите протокол прокси> ")
			if (self.TYPE != "http") and (self.TYPE != "https") and (self.TYPE != "socks4") and (self.TYPE != "socks5"):
				print(self.NAME + coloring("Введенный протокол прокси не поддерживается, ты точно ввел его правильно?", "red"))
				exit(1)



if __name__ == "__main__":
	libInstaller()
	try:
		from modules import proxyscrape, subnets_socket, blocked, weed, \
			removeshit, headers_check, bans_checker, userlink_checker, proxy_parser, \
			countries_2ip, countries_ipinfo, coloring, logwrite
		import colorama
		colorama.init()
		coloring = coloring.coloring
	except Exception as e:
		print(f"Не удалось загрузить все модули/библиотеки: {e}")
		raise e
	else:
		print(coloring("Все модули и библиотеки успешно загружены!", "green"))
	##############
	start = Main()
	start.main()
