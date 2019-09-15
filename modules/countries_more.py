# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import bs4
from requests import get as _get
import urllib3
import json
import backoff
from requests import exceptions
import random
import colorama
colorama.init()
import os
from multiprocessing import Process, Lock, Manager
#import multiprocessing
from modules import logwrite

from modules import coloring
coloring = coloring.coloring
import configparser


class Main():

	def __init__(self, proxy_list, TYPE):
		self.countries = []  # список заблокированных стран
		self.output = []  # прокси на выход
		self.died = []  # мертвые прокси
		self.blocked = []  # заблокированные прокси
		self.input = proxy_list
		self.protocol = TYPE
		self.ASN = []
		# with configparser.ConfigParser() as config:
		# 	config.read("settings.ini")
		# 	self.TIMEOUT = config["COUNTRIES_ADVANCED"]["TIMEOUT"]
		# 	self.MAXTRIES = config["COUNTRIES_ADVANCED"]["MAXTRIES"]
		# 	self.THREADS_MULTIPLIER = config["COUNTRIES_ADVANCED"]["THREADS"]
		# 	self.NAME = config["main"]["NAME"]
		config = configparser.ConfigParser()
		config.read("settings.ini")
		self.TIMEOUT = config.getint("COUNTRIES_ADVANCED", "TIMEOUT")
		self.MAXTRIES = config.getint("COUNTRIES_ADVANCED", "MAXTRIES")
		self.THREADS_MULTIPLIER = config.getint("COUNTRIES_ADVANCED", "THREADS")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		del config

		with open("texts/ASN.txt", mode="r") as file:
			self.ASN = file.read().split()
			try:
				self.ASN.remove("")
			except:
				pass
			print(self.NAME + "ASN-номера загружены успешно!")

	def main_main(self):
		with Manager() as manager:
			lst = manager.list(self.input)  # создание списка проксей для многопотока
			blocked = manager.list(self.blocked)
			output = manager.list(self.output)  # создание списка выходящий проксей 
			died = manager.list(self.died)  # создание списка мертвых проксей
			procs = []  # массив с потоками
			for i in range(0, self.THREADS_MULTIPLIER):
				proc = Process(target=Main.check, args=(self, lst, output, died, blocked,))
				# стартуем!
				proc.start()
				procs.append(proc)

			for pr in procs:
				# присоединение потока к осовному
				pr.join()
			self.output = list(output)
			self.died = list(died)
			self.blocked = list(blocked)

			with open("blocked.txt", mode="w", encoding="UTF-8") as file:
				for i in self.blocked:
					file.write(i + "\n")

			with open("died.txt", mode="w", encoding="UTF-8") as file:
				for i in self.died:
					file.write(i + "\n")

			return self.output

	def check(self, lst, output, died, blocked):
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		while len(lst):
			try:
				# получени информации об айпи прокси 
				i = lst.pop()
				proxy = {"https": self.protocol + "://" + i}
				url = "https://ipinfo.io/{0}/json".format(str(i.split(":")[0]))\
				# создание запроса с обработкой исключений с помощью backoff
				req = backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries = self.MAXTRIES, jitter = None, max_time = (self.TIMEOUT*self.MAXTRIES)+3 )(_get)
				# получение каталога тредов
				answ = json.loads(req(url, verify=False, timeout=self.TIMEOUT, proxies=proxy).text)

			except KeyboardInterrupt:
				print(self.NAME + coloring("Принудительный выход...", "yellow"))
				break
			except IndexError:
				print(self.NAME + coloring("0 проксей в общем списке, выход из потока...", "yellow"))
			except:
				print(self.NAME + coloring("[{0} проксей осталось] ".format(str(len(lst))), "green"
				), end="")
				print(coloring("Нерабочая прокси {0}".format(i), "white"))
				died.append(i)
			else:
				# получение ASN
				try:
					AsnOfProxy = answ["org"].split(" ")[0]
				except Exception as e:
					logwrite.log(e, "countries_more", er=str(answ))
					continue

				for j in self.ASN:
					if AsnOfProxy == j:
						print(self.NAME + coloring("[{0} проксей осталось] ".format(str(len(lst))), "green"), end="")
						print(coloring("Найдена рабочая прокси с запрещенным ASN номером {0} ({1})".format(j, i), "yellow"))
						blocked.append(i)
						break
					else:
						pass
				else:
					print(self.NAME + coloring("[{0} проксей осталось] ".format(str(len(lst))), "green"), end="")
					print(coloring("Найдена рабочая прокси {0}".format(i), "green"))
					output.append(i)



if __name__ == '__main__':
	pass
