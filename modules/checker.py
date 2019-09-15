# -*- coding: utf-8 -*-

from requests import post as _post
from requests import get as _get
import urllib3
import json
import backoff
from requests import exceptions
import random
#mport threading
import colorama
colorama.init()
import os
from multiprocessing import Process, Lock, Manager
import multiprocessing
from modules import coloring
coloring = coloring.coloring
from modules import logwrite

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # отключение уведомления о небезопасном соединении
import configparser


class Check():
	def __init__(self, proxies, protocol, post_check):
		self.proxies = proxies
		self.protocol = protocol
		self.post_check2ch = post_check
		self.output = []
		self.banned = []
		self.died = []

		config = configparser.ConfigParser()
		config.read("settings.ini")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.BOARD = config["CHECKER"]["BOARD"]
		self.MAXTRIES = config.getint("CHECKER", "MAXTRIES")
		self.TIMEOUT = config.getint("CHECKER", "TIMEOUT")
		self.THREADS_MULTIPLIER= config.getint("CHECKER", "THREADS")
		self.WEBFORPING = config["CHECKER"]["WEBFORPING"]
		# self.headers = config.items("HEADERS_CUSTOM")
		# self.headers_2ch = config["HEADERS_2CH"]
		del config
		with open("texts/headers.json") as file:
			hds = json.loads(file.read())
			self.headers_2ch = hds["HEADERS_2CH"]
			self.headers = hds["HEADERS_CUSTOM"]

		with open("texts/usrAgents.txt") as file:
			self.agents = file.read().split("\n")
			while True:
				try:
					self.agents.remove("")
				except:
					break
		self.headers_2ch["Refer"] = "https://2ch.hk/{0}/".format(str(self.BOARD))

	
	def check2ch(self, threads, lst, output, died, banned):
		params = {}
		params["task"] = "report"
		params["board"] = self.BOARD

		while len(lst):
			params["thread"] = threads[random.randint(0, len(threads)-1)] # получение рандомного треда из списка тредов
			heads = self.headers_2ch
			heads["User-Agent"] = self.agents[random.randint(0, len(self.agents)-1)]
			params["comment"] = ''.join(str(random.randint(1000, 10000)))  # комментарий, который видит чмод
			try:
				i = lst.pop()
			except IndexError:
				print("Выход из потока...")
				break
			
			proxy = {"https": self.protocol + "://" + i}
			try:
				req = backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries=self.MAXTRIES, jitter=None, max_time=25)(_post)  # обработка исключений
				# отправка запроса на [данные удалены] для проверки на постинг
				response = json.loads(req("https://5.61.239.35/makaba/makaba.fcgi?json=1", data=params, proxies=proxy, timeout=self.TIMEOUT, headers=heads, verify=False).text)
			except KeyboardInterrupt:
				print(self.NAME + coloring("Принудительный выход...", "yellow"))
				break
			except:
				print(self.NAME + coloring("[{0} проксей осталось] ".format(str(len(lst))), "green"
				), end="")
				print("Нерабочая прокси {0}".format(i))
				died.append(i)
			else:
				print(self.NAME + coloring("[{0} проксей осталось] ".format(str(len(lst))), "green"
				), end="")
				if response['message'] == 'Тред не существует.':
					print(coloring("Найдена прокси в бане {0}".format(i), "red"))
					banned.append(i)
				elif response['message'] == '':
					print(coloring("Найдена незабаненная прокси {0}".format(i), "green"))
					output.append(i)
				else:
					print(coloring("Нестандартный ответ ({0})".format(str(response)), "yellow"))
					
	def get_board(self):
		print(self.NAME + "Получение списка тредов...")
		try:
			# создание запроса с обработкой исключений с помощью backoff
			req = backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries = 10, jitter = None, max_time = 30)(_get)
			# получение каталога тредов
			answ = json.loads(req(''.join(["https://2ch.hk/" + self.BOARD + "/catalog.json"]), verify=False, timeout=30).text)
		except:
			print(self.NAME + 'Ошибка загрузки тредов!')
			exit(0)
		else:
			print(self.NAME + 'Треды загружены успешно!')
		return answ


	def list_of_posts(self):
		'''Обработка каталога и получения номеров треда'''
		list = []
		answer = Check.get_board(self)
		for i in range(0, len(answer)):
			list.append(answer['threads'][i]['num'])
		return list

	def check(self, lst, output, died):
		while len(lst):
			heads = self.headers
			heads["User-Agent"] = self.agents[random.randint(0, len(self.agents)-1)]
			try:
				i = lst.pop()
				proxy = {"https": self.protocol + "://" + i} 
				# обработка исключений
				req = backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries = self.MAXTRIES, jitter = None, max_time = 25)(_get)
				# пингование 2ch.hk, можно поменять на любой живой сайт
				answ = req(''.join(self.WEBFORPING), proxies=proxy, timeout=self.TIMEOUT, headers=heads, verify=False)
			except KeyboardInterrupt:
				print(self.NAME + coloring("Принудительный выход...", "yellow"))
				break
			except:
				print(self.NAME + coloring("[{0} проксей осталось] ".format(str(len(lst))), "green"
				), end="")
				print(coloring("Нерабочая прокси {0}".format(i), "yellow"))
				died.append(i)
			else:
				print(self.NAME + coloring("[{0} проксей осталось] ".format(str(len(lst))), "green"
				), end="")
				print(coloring("Найдена рабочая прокси {0}".format(i), "green"))
				output.append(i)



	def main_main(self):
		with Manager() as manager:
			lst = manager.list(self.proxies)  # создание списка проксей для многопотока
			output = manager.list(self.output)  # создание списка выходящий проксей 
			died = manager.list(self.died)  # создание списка мертвых проксей
			banned = manager.list(self.banned)  # создание списка проксей в бане
			if self.post_check2ch:
				print(self.NAME + "Инициирована проверка на баны.")
				threads_list = Check.list_of_posts(self)
			procs = []  # массив с потоками
			for i in range(0, self.THREADS_MULTIPLIER):
				if self.post_check2ch:
					# создание потока
					proc = Process(target=Check.check2ch, args=(self, threads_list, lst, output, died, banned))
				else:
					# тоже создание потока
					proc = Process(target=Check.check, args=(self, lst, output, died,))
				# стартуем!
				proc.start()
				procs.append(proc)

			for pr in procs:
				# присоединение потока к осовному
				pr.join()
			self.output = list(output)
			self.banned = list(banned)
			self.died = list(died)
		
		# у меня один раз крашнулся модуль проверки, причину я так и не нашел. поэтому пусть этой будет пока тут.
		try:
			print(self.NAME + coloring("Потоки завершились!", "green"))
			# записи в txt
			if self.post_check2ch:
				with open("banned.txt", mode="w", encoding="UTF-8") as file:
					for i in self.banned:
						file.write(i + "\n")
				print(self.NAME + coloring("Записаны прокси в бане ({0}) в banned.txt".format(str(len(self.banned))), "green"))
			with open("died.txt", mode="w", encoding="UTF-8") as file:
				for i in self.died:
					file.write(i + "\n")
				print(self.NAME + coloring("Записаны нерабочие прокси ({0}) в died.txt".format(str(len(self.died))), "green"))
		
		except Exception as e:
			print("Ошибка {0}! Просьба написать на почту если вы видите это сообщение!".format(e))
			logwrite.log(e, "checker", name="Ошибка записи в текстовик")

		return self.output


if __name__ == '__main__':
	pass