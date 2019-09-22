# -*- coding: utf-8 -*-
from modules import logwrite
import backoff
import requests
from requests import get as _get
from requests import exceptions
from multiprocessing import Process, Lock, Manager
import multiprocessing
import urllib3
import json
import colorama
colorama.init()
import urllib3
from modules import coloring
coloring = coloring.coloring
import configparser

class Main(object):
	"""docstring for Main"""
	def __init__(self, proxies):
		super(Main, self).__init__()
		self.proxies = proxies

		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.token = config["2IP"]["TOKEN"]
		self.threads = config.getint("2IP", "THREADS")
		self.unknown = config.getboolean("2IP", "UNKNOWNOUT")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		del config


		self.headers = {
		"X-API-Token": self.token,
		"User-Agent": "curl/7.64.0",
		}
		with open("texts/countries.txt") as file:
			self.countries = file.read().split("\n")
			while True:
				try:
					self.countries.remove("")
				except:
					break

	def filtering(self, proxyList, output):
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # отключение уведомления о небезопасном соединении
		while len(proxyList):
			try:
				i = proxyList.pop()
			except:
				print(self.NAME + coloring("Выход из потока...", "green"))
				break
			try:
				ses = requests.Session()
				answ = ses.get("https://2ip.ru/api/v1.0/geo/" + i.split(":")[0], headers=self.headers, timeout=10, verify=False).json()
				ses.__exit__()
			except KeyboardInterrupt:
				print(self.NAME + coloring("Принудительный выход...", "yellow"))
				break
			except Exception as e:
				logwrite.log(e, "ip2", name="В отправке")
				print(self.NAME + coloring("Ошибка соединения с сервером! Проверьте подключения к интернету или снизьте потоки!", "red"))
				continue
			else:
				try:
					answ = answ["info"]["country"]
				except Exception as e:
					print(self.NAME + coloring("Неизвестная страна!", "yellow"))
					if self.unknown:
						output.append(i)
					else:
						pass
					break
					#print(self.NAME + coloring("Неизвестный ответ 2ip!", "yellow"))
					#logwrite.log(e, "ip2", name="неизвестный ответ", answer=answ)
				for country in self.countries:
					if answ == country:
						print(self.NAME + coloring("Найден айпи из запрещенной страны! {0}".format(i.split(":")[0]), "yellow"))
						break
				else:
					output.append(i)

	def start(self):
		out = []
		with Manager() as manager:
			proxyList = manager.list(self.proxies)
			output = manager.list(out)
			procs = []
			for i in range(0, self.threads):
				proc = Process(target=self.filtering, args=(proxyList, output))
				proc.start()
				procs.append(proc)
			for proc in procs:
				proc.join()
			self.proxies = list(output)
		return self.proxies










if __name__ == '__main__':
	a =["228.228.228.228"]
	start = Main(a)
		