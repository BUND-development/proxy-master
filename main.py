# -*- coding: utf-8 -*-

import sys
import json
import os

def cls():
	'''Очистка консоли'''
	os.system('cls' if os.name=='nt' else 'clear')

def coloring(string, color):
	'''Мой мини-модуль для раскрашивания текста'''
	if color == "red":
		string = "\x1b[31m" + string + "\x1b[0m"
	elif color == "green":
		string = "\x1b[32m" + string + "\x1b[0m"
	elif color == "yellow":
		string = "\x1b[33m" + string + "\x1b[0m"
	elif color == "blue":
		string = "\x1b[34m" + string + "\x1b[0m"
	else:
		pass
	return string

try:
	os.system("pip install requests pysocks urllib3 bs4 colorama lxml pygeoip backoff" if os.name=="nt" else "pip3 install --user requests pysocks urllib3 bs4 colorama lxml pygeoip backoff")
except:
	pass
finally:
	cls()


try:
	from modules import parser, proxyscrape, subnets, blocked, weed, checker, countries_more
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

class Main():
	
	def __init__(self, *args, **kwargs):
		super().__init__()
		out_logo()
		self.export = []  # прокси на выход
		with open("settings.ini", mode="r") as file:
			settings = json.load(file)
			self.FILENAME_EXPORT = settings["FILENAME_EXPORT"]  # файл с прокси на выходе
			self.NORMALINPUT = settings["NORMALINPUT"]  # ввод аргументов
			self.PARSE = settings["PARSE"] # парсить прокси
			self.SUBNETS = settings["SUBNETS"] # фильтрование по подсетям
			self.BLACKLIST = settings["BLACKLIST"]  # блеклист айпи
			self.COUNTRIES = settings["COUNTRIES"]  # фильтровать по странам
			self.CHECK = settings["CHECK"] # проверять на работоспособность
			self.CHECKON2CH = settings["CHECKON2CH"]  # проверять на бан на 2ch.hk
			self.PROTOCOLOUT = settings["PROTOCOLOUT"]  # записывать прокси в формате протокол://прокси:порт
			self.CHECK_ADVANCED = settings["CHECK_ADVANCED"]  # использовать ли сайт 2ip.io как фильтр стран и провайдеров
			self.NAME = "\x1b[32m" + "[P-M]" + "\x1b[0m"
		
	def main(self):
		Main.geting(self)
		print(self.NAME + coloring("Ввод получен!", "green"))
		with open("input-proxies.txt", mode="r", encoding="UTF-8") as file:
			self.export = file.read().split("\n")
			try:
				self.export.remove("")
			except:
				pass
		
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
		
		if self.SUBNETS:
			print(self.NAME + coloring("Фильтрация подсетей начата...", "green"))
			filtering = subnets.FilteringSubnets(self.export)
			self.export = filtering.start()
			print(self.NAME + coloring("Фильтрация подсетей закончена.", "green"))
		
		if self.BLACKLIST:
			print(self.NAME + coloring("Удаление одинаковых айпи началось...", "green"))
			filtering = blocked.Blocked(self.export)
			self.export = filtering.start()
			print(self.NAME + coloring("Удаление одинаковых айпи закончено.", "green"))

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
				with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
					file.write("=====================\n{0}, type:{1}\n".format(str(e), self.TYPE))
			else:
				print(self.NAME + coloring("Фильтрация по ASN закончена.", "green"))

		if self.CHECK:
			print(self.NAME + coloring("Проверка на рабоспособность началась...", "green"))
			filtering = checker.Check(self.export, self.TYPE, self.CHECKON2CH)
			try:
				self.export = filtering.main_main()
			except KeyboardInterrupt:
				print(self.NAME + "Принудительный выход, сохранение...")
			except:
				print(self.NAME + coloring("Ошибка модуля проверки на постинг, просьба написать об этом на почту", "red"))
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
		with open("settings.ini", mode="r", encoding="utf-8") as file:
			settings = json.load(file)

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
	start = Main()
	start.main()
