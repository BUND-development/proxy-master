# -*- coding: utf-8 -*-

from requests import post as _post
from requests import get as _get
import urllib3
import json
import backoff
from requests import exceptions
import random
import threading
import colorama
colorama.init()
import os
from multiprocessing import Process, Lock, Manager
import multiprocessing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#l = threading.Lock()
#l = Lock()

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

class Check():
	def __init__(self, proxies, protocol, post_check):
		self.proxies = proxies
		self.protocol = protocol
		self.post_check2ch = post_check  
		self.BOARD = "b"
		self.output = []
		self.MAXTRIES = 3
		self.TIMEOUT = 15
		self.THREADS_MULTIPLIER = 12
		self.headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
		"Origin": "https://2ch.hk",
		"Referer": "https://2ch.hk/b/",
		"Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
		"Connection": "close",
		}

	def check2ch(self, threads, lst, output):
		#print(str(os.getpid()))
		params = {}
		params["task"] = "report"
		params["board"] = self.BOARD
		params["thread"] = threads[random.randint(0, len(threads)-1)] # получение рандомного треда из списка тредов
		params["comment"] = ''.join(str(random.randint(1000, 10000)))

		while len(lst):
			if len(lst) == 0:
				print("Выход из потока...")
			i = lst.pop()
			proxy = {"https": self.protocol + "://" + i}
			try:
				req = backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries=self.MAXTRIES, jitter=None, max_time=25)(_post)
				response = json.loads(req("https://5.61.239.35/makaba/makaba.fcgi?json=1", data=params, proxies=proxy, timeout=self.TIMEOUT, headers=self.headers, verify=False).text)
			except KeyboardInterrupt:
				print(coloring("Принудительный выход...", "yellow"))
				break
			except:
				print("Нерабочая прокси {0}".format(i))
			else:
				if response['message'] == 'Тред не существует.':
					print(coloring("Найдена прокси в бане {0}".format(i), "red"))
				elif response['message'] == '':
					print(coloring("Найдена незабаненная прокси {0}".format(i), "green"))
					output.append(i)
				else:
					print(coloring("Нестандартный ответ ({0})".format(str(response)), "red"))
					
	def get_board(self):
		print("Получение списка тредов...")
		try:
			# создание запроса с обработкой исключений с помощью backoff
			req = backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries = 10, jitter = None, max_time = 30)(_get)
			answ = json.loads(req(''.join(["https://2ch.hk/" + self.BOARD + "/catalog.json"]), verify=False, timeout=5).text)
		except:
			print('Ошибка загрузки тредов!')
			exit(0)
		else:
			print('Треды загружены успешно!')
		return answ


	def list_of_posts(self):
		list = []
		answer = Check.get_board(self)
		for i in range(0, len(answer)):
			list.append(answer['threads'][i]['num'])
		return list

	def check(self, lst, output):
		while len(lst):
			try:
				i = lst.pop()
				proxy = {"https": self.protocol + "://" + i} 
				req = backoff.on_exception(backoff.expo, exceptions.ConnectionError, max_tries = self.MAXTRIES, jitter = None, max_time = 25)(_get)
				answ = req(''.join(["google.com"]), proxies=proxy, timeout=self.TIMEOUT, headers=self.headers, verify=False)
			except KeyboardInterrupt:
				print(coloring("Принудительный выход...", "yellow"))
				break
			except:
				print(coloring("Нерабочая прокси {0}".format(i), "yellow"))
			else:
				print(coloring("Найдена рабочая прокси {0}".format(i), "green"))
				output.append(i)



	def main_main(self):
		with Manager() as manager:
			lst = manager.list(self.proxies)
			output = manager.list(self.output)
			if self.post_check2ch:
				print("Инициирована проверка на баны.")
				threads_list = Check.list_of_posts(self)
			procs = []
			for i in range(0, self.THREADS_MULTIPLIER):
				if self.post_check2ch:
					proc = Process(target=Check.check2ch, args=(self, threads_list, lst, output,))
				else:
					proc = Process(target=Check.check, args=(self, lst, output))
				proc.start()
				procs.append(proc)

			for pr in procs:
				pr.join()
			self.output = list(output)
		print("Все потоки пройдены!")


		return self.output


if __name__ == '__main__':
	start = Check.start("", "", "")