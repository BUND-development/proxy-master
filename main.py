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



try:
	from modules import parser, proxyscrape, subnets, blocked, weed
	import colorama
	colorama.init()
	import sys
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
	print(r"  __       __                                                                                              ")
	print(r" /_ |     /_ |                                                                                             ")
	print(r"  | |      | |                                                                                             ")
	print(r"  | |      | |                                                                                             ")
	print(r"  | |  _   | |                                                                                             ")
	print(r"  |_| (_)  |_|                                                                                             ")
	print("\n\n")

class Main():
	
	def __init__(self, *args, **kwargs):
		super().__init__()
		out_logo()
		self.export = []  # прокси на выход
		self.FILENAME_EXPORT = "proxies.txt"  # файл с прокси на выходе
		self.NORMALINPUT = False
		self.PARSE = True  # парсить прокси
		self.SUBNETS = True  # фильтрование по подсетям
		self.BLACKLIST = True  # блеклист айпи
		self.COUNTRIES = True  # фильтровать по странам
		
	def main(self):
		Main.geting(self)
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
		
		with open(self.FILENAME_EXPORT, mode="w", encoding="UTF-8") as file:
			try:
				self.export.remove("")
			except:
				pass
			print("Всего было обработано {0} прокси-серверов.".format(str(len(self.export))))
			for i in self.export:
				file.write(str(i) + "\n")

	def geting(self):
		if self.NORMALINPUT:
			#self.TYPE = sys.argv[1]  # тип прокси
			#self.SUBNETS = bool(sys.argv[2])  # фильтрование по подсетям
			#self.BLACKLIST = bool(sys.argv[3])  # блеклист айпи
			#self.WORKCHECK = bool(sys.argv[2])  # проверка на рабоспособность
			pass
		# статичные параметры для дебага, пока не используются
		elif True:  
			self.TYPE = "http"  # тип прокси
			#self.SUBNETS = 1  # фильтрование по подсетям
			#self.BLACKLIST = 1  # блеклист айпи
			self.WORKCHECK = 1  # проверка на рабоспособность
			pass
		else:
			#self.TYPE = input("Тип соединения (https/http/socks4/socks5)> ")  # тип прокси
			#self.SUBNETS = bool(input("Фильтровать по подсетям (0 - нет, 1 - да)> "))  # фильтрование по подсетям
			#self.BLACKLIST = bool(input("Использовать блеклист айпи (0 - нет, 1 - да)> "))  # блеклист айпи
			#self.WORKCHECK = bool(input("Проверять на рабоспособность (0 - нет, 1 - да)> "))  # проверка на рабоспособность
			pass


if __name__ == "__main__":
	start = Main()
	start.main()
