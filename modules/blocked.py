# -*- coding: utf-8 -*-



import json
import colorama
colorama.init()
from modules import coloring
coloring = coloring.coloring
from modules import logwrite
import configparser



class Blocked():
	'''
	Удаление проксей из блеклиста
	'''
	def __init__(self, proxies):
		self.proxies = proxies
		self.blacklist = []
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.NAME = "\x1b[32m" +  config["main"]["NAME"] + "\x1b[0m"
		del config
		######################################################
		with open("texts/blacklist.txt", mode="r") as file:
			self.blacklist = file.read().split("\n")
			while True:
				try:
					self.blacklist.remove("")
				except:
					break
		#####################################	
		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i].split(":")  # разделение по айпи и портам

	def start(self):
		print(self.NAME + coloring("Фильтрация проксей началась...", "green"))
		self.proxies = self.remove_blocked(self.proxies)
		####################################
		for i in range(0, len(self.proxies)):
			try:
				self.proxies[i] = self.proxies[i][0] + ":" + self.proxies[i][1]
			except Exception as e:
				print(self.NAME + coloring("Непредвиденная ошибка: {0}".format(e), "red"))
				logwrite.log(e, "blocked", name="в соединение проксей")
			continue
		print(self.NAME + coloring("Фильтрация проксей закончена.", "green"))
		return self.proxies

	def remove_blocked(self, proxylist):
		output = []
		for i in proxylist:
			for i2 in self.blacklist:
				if i[0] == i2 or i == '':
					print(self.NAME + "Найдена прокси, находящийся в айпи-блеклисте {0}".format(i[0] + ":" + i[1]))
					break
			else:
				output.append(i)
		return output



if __name__ == '__main__':
	pass