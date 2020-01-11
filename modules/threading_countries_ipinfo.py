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
		self.bad = []
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
					print(self.checker.NAME + coloring(f"[{self.proxies.getStat()}]Найдена прокси с блеклист ASN: {proxy}", "yellow"))
					with self.lock:
						self.proxies.bad.append(proxy)
			else:
				print(self.checker.NAME + coloring(f"[{self.proxies.getStat()}]Нерабочая прокси: {proxy}", "white"))
				with self.lock:
					self.proxies.died.append(proxy)



class Check():
	'''запрос'''
	def __init__(self):
		'''init'''
		config = configparser.ConfigParser()
		####################################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.TIMEOUT = connect=config.getint("COUNTRIES_ADVANCED", "TIMEOUT")
		self.MAXTRIES = config.getint("COUNTRIES_ADVANCED", "MAXTRIES")
		self.TASKS = config.getint("COUNTRIES_ADVANCED", "TASKS")
		self.UNKNOWN = config.getboolean("COUNTRIES_ADVANCED", "UNKNOWN")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		#####################################
		with open("texts/ASN.txt", mode="r") as file:
			self.ASN = file.read().split()
			while True:
				try:
					self.ASN.remove("")
				except:
					break
			print(self.NAME + "ASN-номера загружены успешно!")
		self.send = backoff.on_exception(backoff.expo, Exception, max_tries = self.MAXTRIES, jitter = None, max_time = 120)(requests.get)
		#####################################

	def request(self, proxy, protocol):
		'''Отправка запроса'''
		proxies = {
		"http": f"{protocol}://{proxy}",
		"https": f"{protocol}://{proxy}"
		}
		try:
			_ = proxy.split(":")[0]
			answer = json.loads(self.send(f"http://ipinfo.io/{_}/json", proxies=proxies, verify=False, timeout=self.TIMEOUT).text)
		except Exception as e:
			return False, None
		else:
			return True, answer

	def answerStatus(self, answer):
		'''
		Анализ ответа
		'''
		try:
			answer = answer["org"].split(" ")[0]
		except:
			if self.UNKNOWN:
				return True
			else:
				return False
		for i in self.ASN:
			if answer == i:
				break
			else:
				return True
			return False



@tools.errorsCap
def main(proxies, protocol):
	'''ipinfo threading main'''
	checker = Check()
	lock = threading.Lock()
	_proxies = Proxies(proxies)
	_threads = checker.TASKS
	flag = threading.Event()
	threads = []
	print(checker.NAME + coloring("Началась проверка на ASN-номера через ipinfo...", "green"))
	##############################
	for i in range(0, _threads+1):
		_ = CheckerThread(_proxies, protocol, checker, lock, flag)
		threads.append(_)
		_.setDaemon(True)
		_.start()
	#########
	try:
		for i in threads:
			i.join()
	except KeyboardInterrupt:
		print(checker.NAME + coloring("Проверка отменена! Завершение всех потоков...", "yellow"))
		flag.set()
		while True:
			threads = threading.enumerate()
			if len(threads) > 1:
				time.sleep(2)
			else:
				break
	except Exception as e:
		logwrite.log(e, "main threading_countries_ipinfo")
	else:
		with open("trashproxies/died.txt", mode="a", encoding="UTF-8") as file:
			for i in _proxies.died:
				file.write(i + "\n")
		#########################################################################
		with open("trashproxies/badASN.txt", mode="a", encoding="UTF-8") as file:
			for i in _proxies.bad:
				file.write(i + "\n")
		##########################################################
		print(checker.NAME + coloring(f"Записаны нерабочие прокси в trashproxies/died.txt {str(len(_proxies.died))} единиц.", "green"))
		print(checker.NAME + coloring(f"Записаны прокси с ASN из блек-листа в trashproxies/badASN.txt {str(len(_proxies.bad))} единиц.", "green"))
		print(checker.NAME + coloring("Проверка ASN закончилась.", "green"))
	return _proxies.green



if __name__ == '__main__':
	pass