# -*- coding: utf-8 -*-

import backoff
import configparser
import copy
from urllib3 import disable_warnings, exceptions
import threading
import requests
import random
from modules import logwrite, coloring, tools
coloring = coloring.coloring
import json
import string
import time
disable_warnings(exceptions.InsecureRequestWarning)


class Proxies():
	def __init__(self, proxies):
		self.input = proxies
		self.green = []
		self.banned = []
		self.died = []

	def getStat(self):
		'''Получение статы'''
		return f"{str(len(self.input))}/{str(len(self.green))}"



class CheckerThread(threading.Thread):
	'''Класс чекер'''
	def __init__(self, proxies, protocol, checker, lock, flag):
		'''init'''
		threading.Thread.__init__(self)
		self.proxies = proxies
		self.protocol = protocol
		self.checker = checker
		self.lock = lock
		self.flag = flag

	@tools.errorsCap
	def run(self):
		'''Запуск'''
		while True:
			if self.flag.is_set():
				break
			#########
			with self.lock:
				try:
					proxy = self.proxies.input.pop()
				except IndexError:
					break
				except Exception as e:
					raise e
			#############################
			status, answer = self.checker.request(proxy, self.protocol)
			############
			if status:
				if self.checker.answerStatus(answer):
					print(self.checker.NAME + coloring(f"[{self.proxies.getStat()}]Найдена рабочая прокси: {proxy}", "green"))
					with self.lock:
						self.proxies.green.append(proxy)
				else:
					print(self.checker.NAME + coloring(f"[{self.proxies.getStat()}]Найдена забаненная прокси: {proxy}", "yellow"))
					with self.lock:
						self.proxies.banned.append(proxy)
			else:
				print(self.checker.NAME + coloring(f"[{self.proxies.getStat()}]Нерабочая прокси: {proxy}", "white"))
				with self.lock:
					self.proxies.died.append(proxy)



class Check():
	'''запрос'''
	def __init__(self):
		'''init'''
		config = configparser.ConfigParser()
		self.url = "http://2ch.hk/makaba/makaba.fcgi?json=1"
		####################################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.MAXTRIES = config.getint("BANS_CHECKER", "MAXTRIES")
		self.TIMEOUT = config.getint("BANS_CHECKER", "TIMEOUT")
		self.TASKS = config.getint("BANS_CHECKER", "TASKS")
		self.BOARD = config.get("BANS_CHECKER", "BOARD")
		self.PROXY = config.get("main", "PROXY")
		self.send = backoff.on_exception(backoff.expo, Exception, max_tries = self.MAXTRIES, jitter = None, max_time = 120)(requests.post)
		#####################################
		with open("texts/headers.json") as file:
			hds = json.loads(file.read())
			self.headers_2ch = hds["HEADERS_2CH"]
		##########################################
		with open("texts/usrAgents.txt") as file:
			self.agents = file.read().split("\n")
			while True:
				try:
					self.agents.remove("")
				except:
					break
		##########################################
		self.headers_2ch["Refer"] = f"https://2ch.hk/{self.BOARD}/"
		###########################
		# список тредов
		self.ThreadList = []
		self.ThreadList = self.get_board()

	def request(self, proxy, protocol):
		'''Отправка запроса'''
		thread = self.ThreadList[random.randint(0, len(self.ThreadList)-1)]
		proxies = {
		"http": f"{protocol}://{proxy}",
		"https": f"{protocol}://{proxy}"
		}
		params = {
					'task': 'report',
					'board': self.BOARD,
					'thread': thread,
					'comment': ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(5, 20))),
					'posts': thread
					}
		headers = copy.deepcopy(self.headers_2ch)
		headers["User-Agent"] = self.agents[random.randint(0, len(self.agents)-1)]
		try:
			answer = json.loads(self.send(self.url, proxies=proxies, verify=False, params=params, timeout=self.TIMEOUT, headers=headers).text)
		except Exception as e:
			return False, None
		else:
			return True, answer

	def answerStatus(self, response):
		'''
		Анализ ответа на [данные удалены]
		'''
		if response["message"] == 'Тред не существует.':
			return False
		elif response['message'] == '':
			return True
		else:
			print(self.NAME + coloring(f"Нестандартный ответ: {str(response)}", "red"))
			return False

	def get_board(self):
		'''Получение списка тредов'''
		print(self.NAME + "Получение списка тредов...")
		if self.PROXY != "0":
			proxies = {
			"https": self.PROXY,
			"http": self.PROXY
			}
		else:
			proxies = None
		#######################
		answ = None
		while True:
			try:
				req = backoff.on_exception(backoff.expo, Exception, max_tries = 10, jitter = None, max_time = 30)(requests.get)
				answ = json.loads(req(''.join(["http://2ch.hk/" + self.BOARD + "/catalog.json"]), verify=False, headers=self.headers_2ch, timeout=30, proxies=proxies).text)
			except Exception as e:
				print(self.NAME + f'Ошибка загрузки тредов {e}')
				input(self.NAME + "Проверьте подключение к интернету и нажмите любую клавишу...")
				continue
			else:
				print(self.NAME + 'Треды загружены успешно!')
				break
		return self.list_of_posts(answ)

	@staticmethod
	def list_of_posts(answer):
		'''
		Обработка каталога и получения номеров треда
		'''
		lst = []
		for i in range(0, len(answer)):
			lst.append(answer['threads'][i]['num'])
		return lst

@tools.errorsCap
def main(proxies, protocol):
	'''bans checker threading main'''
	checker = Check()
	lock = threading.Lock()
	_proxies = Proxies(proxies)
	_threads = checker.TASKS
	flag = threading.Event()
	threads = []
	print(checker.NAME + coloring("Проверка на баны началась...", "green"))
	##############################
	for i in range(0, _threads+1):
		_ = CheckerThread(_proxies, protocol, checker, lock)
		threads.append(_)
		_.setDaemon(True)
		_.start()
	#########
	try:
		for i in threads:
			i.join()
	except KeyboardInterrupt:
		print(checker.NAME + coloring("Проверка отменена!", "yellow"))
		flag.set()
		while True:
			threads = threading.enumerate()
			if len(threads) > 1:
				time.sleep(2)
			else:
				break
	except Exception as e:
		logwrite.log(e, "main threading_ban_checker")
	else:
		print(checker.NAME + coloring("Проверка на баны закончена!", "green"))
	with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
		for i in _proxies.died:
			file.write(i + "\n")
	#########################################################################
	with open("trashproxies/banned.txt", mode="a", encoding="UTF-8") as file:
		for i in _proxies.banned:
			file.write(i + "\n")
	##########################################################
	print(checker.NAME + coloring(f"Записаны нерабочие прокси в trashproxies/died.txt {str(len(_proxies.died))} единиц.", "green"))
	print(checker.NAME + coloring(f"Записаны забаненные прокси в trashproxies/banned.txt {str(len(_proxies.banned))} единиц.", "green"))
	return _proxies.green



if __name__ == '__main__':
	pass