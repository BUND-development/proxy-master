# -*- coding: utf-8 -*-

import sys
import json
import os
import configparser

def out_logo():
	print(r"  _____    _____     ____   __   __ __     __      __  __               _____   _______   ______   _____   ")
	print(r" |  __ \  |  __ \   / __ \  \ \ / / \ \   / /     |  \/  |     /\      / ____| |__   __| |  ____| |  __ \  ")
	print(r" | |__) | | |__) | | |  | |  \ V /   \ \_/ /      | \  / |    /  \    | (___      | |    | |__    | |__) | ")
	print(r" |  ___/  |  _  /  | |  | |   > <     \   /       | |\/| |   / /\ \    \___ \     | |    |  __|   |  _  /  ")
	print(r" | |      | | \ \  | |__| |  / . \     | |        | |  | |  / ____ \   ____) |    | |    | |____  | | \ \  ")
	print(r" |_|      |_|  \_\  \____/  /_/ \_\    |_|        |_|  |_| /_/    \_\ |_____/     |_|    |______| |_|  \_\ ")
	print("")
	print(r"  __       _  _   ")
	print(r" /_ |     | || |  ")
	print(r"  | |     | || |_ ")
	print(r"  | |     |__   _|")
	print(r"  | |  _     | |  ")
	print(r"  |_| (_)    |_|  ")
	print("\n")             
	print("\n\n")

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



class Main():
	
	def __init__(self, *args, **kwargs):
		super().__init__()
		out_logo()
		#self.NAME = "\x1b[32m" + "[P-M]" + "\x1b[0m"
		self.export = []  # прокси на выход
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.PARSE = config.getboolean("modules", "PARSE")
		self.SUBNETS = config.getboolean("modules", "SUBNETS")
		self.BLACKLIST = config.getboolean("modules", "BLACKLIST")
		self.CHECK = config.getboolean("modules", "CHECK")
		self.CHECKON2CH = config.getboolean("modules", "CHECKON2CH")
		self.CHECK_ADVANCED = config.getboolean("modules", "CHECK_ADVANCED")
		self.SAME_FILTERING = config.getboolean("modules", "SAME_FILTERING")
		self.CHECK2IP = config.getboolean("modules", "CHECK2IP")
		self.COUNTRIES = config.getboolean("modules", "COUNTRIES")
		self.CHECK2IP_CODES = config.getboolean("modules", "CHECK2IP_CODES")

		self.PROTOCOLOUT = config.getboolean("main", "PROTOCOLOUT")
		self.FILENAME_EXPORT = config["main"]["FILENAME_EXPORT"]
		self.NORMALINPUT = config.getboolean("main", "NORMALINPUT")
		self.FILTERINGBAD = config.getboolean("main", "FILTERINGBAD")
		self.NAME = "\x1b[32m" +  config["main"]["NAME"] + "\x1b[0m"
		del config
	
	#@decor
	def main(self):
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
			proxy1 = parser.Parsing()  # инициализация класса парсинга
			self.export.extend(proxy1.parsing())  # парсинг
			print(self.NAME + "Получение проксей из api-модулей...")
			proxy2 = proxyscrape.ProxyScrape()  # инициация класса модуля апи
			_ = proxy2.start()  # получение проксей
			print(self.NAME + coloring(
				"Получено {0} проксей из модуля {1}".format(str(len(_)), proxy2.__dict__["modulename"]),
				"green"
				))
			self.export.extend(_)  # добавление проксей
		if self.FILTERINGBAD:
			print(self.NAME + coloring("Удаление невалидных проксей...", "green"))
			filtering = removeshit.Main(self.export, self.SAME_FILTERING)
			self.export = filtering.start()
			print(self.NAME + coloring("Удаление невалидных проксей закончено.", "green"))
		
		if self.BLACKLIST:
			print(self.NAME + coloring("Фильтрация проксей началась...", "green"))
			filtering = blocked.Blocked(self.export)
			self.export = filtering.start()
			print(self.NAME + coloring("Фильтрация проксей началась.", "green"))

		if self.SUBNETS:
			print(self.NAME + coloring("Фильтрация подсетей начата...", "green"))
			filtering = subnets.FilteringSubnets(self.export)
			self.export = filtering.start()
			print(self.NAME + coloring("Фильтрация подсетей закончена.", "green"))

		if self.CHECK2IP or self.CHECK2IP_CODES:
			print(self.NAME + coloring("Фильтрация по 2ip началась...", "green"))
			filtering = ip2.Main(self.export)
			self.export = filtering.start()
			print(self.NAME + coloring("Фильтрация по 2ip закончена.", "green"))

		if self.COUNTRIES:
			print(self.NAME + coloring("Фильтрация по странам началась...", "green"))
			self.export = weed.weed(self.export)
			print(self.NAME + coloring("Фильтрация по странам закончена.", "green"))

		if self.CHECK_ADVANCED:
			print(self.NAME + coloring("Фильтрация по ASN началась...", "green"))
			filtering = countries_more.Main(self.export, self.TYPE)
			try:
				self.export = filtering.main_main()
			except KeyboardInterrupt:
				print(self.NAME + "Принудительный выход, сохранение...")
			except Exception as e:
				print(self.NAME + coloring("Ошибка модуля улучшенного фильтра айпи, просьба отправить BUGREPORT", "red"))
				logwrite.log(e, "main", line="CHECK_ADVANCED")
			else:
				print(self.NAME + coloring("Фильтрация по ASN закончена.", "green"))

		if self.CHECK:
			print(self.NAME + coloring("Проверка на рабоспособность началась...", "green"))
			filtering = checker.Check(self.export, self.TYPE, self.CHECKON2CH)
			try:
				self.export = filtering.main_main()
			except KeyboardInterrupt:
				print(self.NAME + "Принудительный выход, сохранение...")
			except Exception as e:
				print(self.NAME + coloring("Ошибка модуля проверки на постинг, просьба написать об этом на почту", "red"))
				logwrite.log(e, "main", line="CHECK")
			else:
				print(self.NAME + coloring("Проверка на рабоспособность закончена.", "green"))

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
	try:
		from modules import logwrite
		from modules import lib_installer
		from modules import coloring
		coloring = coloring.coloring
	except:
		pass
	try:
		from modules import parser, proxyscrape, subnets, blocked, weed, checker, countries_more, ip2, removeshit
		import colorama
		colorama.init()
	except Exception as e:
		with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
			file.write("=====================\n{0}\n".format(str(e)))
		print(coloring("Не удалось загрузить все модули/библиотеки!", "red"))
		exit(1)
	except:
		print(coloring("Не удалось загрузить все модули/библиотеки!", "red"))
		exit(1)
	else:
		print(coloring("Все модули и библиотеки успешно загружены!", "green"))


	start = Main()
	start.main()
