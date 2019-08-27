# -*- coding: utf-8 -*-



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

from modules import checker

try:
	from modules import parser, proxyscrape, subnets, blocked, weed, checker
	import colorama
	colorama.init()
	import sys
	import json
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
	print(r"  __       ____   ")
	print(r" /_ |     |___ \  ")
	print(r"  | |       __) | ")
	print(r"  | |      |__ <  ")
	print(r"  | |  _   ___) | ")
	print(r"  |_| (_) |____/  ")          
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
		
	def main(self):
		Main.geting(self)
		print(coloring("Ввод получен!", "green"))
		with open("input-proxies.txt", mode="r", encoding="UTF-8") as file:
			self.export = file.read().split("\n")
			try:
				self.export.remove("")
			except:
				pass
		
		if self.PARSE:
			proxy1 = parser.Parsing()  # инициализация класса парсинга
			self.export.extend(proxy1.parsing())  # парсинг
			print("Получение проксей из api-модулей...")
			proxy2 = proxyscrape.ProxyScrape()  # инициация класса модуля апи
			_ = proxy2.start()  # получение проксей
			print(coloring(
				"Получено {0} проксей из модуля {1}".format(str(len(_)), proxy2.__dict__["modulename"]),
				"green"
				))
			self.export.extend(_)  # добавление проксей
		
		if self.SUBNETS:
			print(coloring("Фильтрация подсетей начата...", "green"))
			filtering = subnets.FilteringSubnets(self.export)
			self.export = filtering.start()
			print(coloring("Фильтрация подсетей закончена.", "green"))
		
		if self.BLACKLIST:
			print(coloring("Удаление одинаковых айпи началось...", "green"))
			filtering = blocked.Blocked(self.export)
			self.export = filtering.start()
			print(coloring("Удаление одинаковых айпи закончено.", "green"))

		if self.COUNTRIES:
			print(coloring("Фильтрация по странам началась...", "green"))
			self.export = weed.weed(self.export)
			print(coloring("Фильтрация по странам закончена.", "green"))

		if self.CHECK:
			print(coloring("Проверка на рабоспособность началась...", "green"))
			filtering = checker.Check(self.export, self.TYPE, self.CHECKON2CH)
			#self.export = filtering.main_main()
			try:
				self.export = filtering.main_main()
			except KeyboardInterrupt:
				print("Принудительный выход, сохранение...")
			except:
				print(coloring("Ошибка модуля проверки на постинг, просьба написать об этом на почту", "red"))
			else:
				print(coloring("Проверка на рабоспособность закончена.", "green"))

		with open(self.FILENAME_EXPORT, mode="w", encoding="UTF-8") as file:
			print("", end="\n\n")
			try:
				self.export.remove("")
			except:
				pass
			print("Всего {0} прокси-серверов.".format(str(len(self.export))))
			for i in self.export:
				file.write(str(i) + "\n")

	def geting(self):
		with open("settings.ini", mode="r", encoding="utf-8") as file:
			settings = json.load(file)



		if self.NORMALINPUT:
			try:
				self.TYPE = sys.argv[1]
			except IndexError:
				print(coloring("Ты забыл написать параметр командной строки!", "red"))
				exit(1)
			if (sys.argv[1] != "http") and (sys.argv[1] != "https") and (sys.argv[1] != "socks4") and (sys.argv[1] != "socks5"):
				print(coloring("Введенный протокол прокси не поддерживается, ты точно ввел его правильно?", "red"))
				exit(1)
			# self.PARSE = True # парсить прокси
			# self.SUBNETS = True  # фильтрование по подсетям
			# self.BLACKLIST = True  # блеклист айпи
			# self.COUNTRIES = True  # фильтровать по странам
			# self.CHECK = False # проверять на работоспособность
			# self.CHECKON2CH = True  # проверять на бан на 2ch.hk
		# статичные параметры для дебага, пока не используются
		# elif False:  
		# 	self.TYPE = "http"  # тип прокси
		# 	self.PARSE = False  # парсить прокси
		# 	self.SUBNETS = True  # фильтрование по подсетям
		# 	self.BLACKLIST = True  # блеклист айпи
		# 	self.COUNTRIES = True  # фильтровать по странам
		# 	self.CHECK = True  # проверять на работоспособность
		# 	self.CHECKON2CH = True  # проверять на бан на 2ch.hk
		else:
			self.TYPE = input("Введите протокол прокси> ")
			if (self.TYPE != "http") and (self.TYPE != "https") and (self.TYPE != "socks4") and (self.TYPE != "socks5"):
				print(coloring("Введенный протокол прокси не поддерживается, ты точно ввел его правильно?", "red"))
				exit(1)
			# self.PARSE = True  # парсить прокси
			# self.SUBNETS = True  # фильтрование по подсетям
			# self.BLACKLIST = True  # блеклист айпи
			# self.COUNTRIES = True  # фильтровать по странам
			# self.CHECK = False  # проверять на работоспособность
			# self.CHECKON2CH = True  # проверять на бан на 2ch.hk
		# self.PARSE = True # парсить прокси
		# self.SUBNETS = True  # фильтрование по подсетям
		# self.BLACKLIST = True  # блеклист айпи
		# self.COUNTRIES = True  # фильтровать по странам
		# self.CHECK = True # проверять на работоспособность
		# self.CHECKON2CH = True  # проверять на бан на 2ch.hk
			


if __name__ == "__main__":
	start = Main()
	start.main()
