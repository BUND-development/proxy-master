# -*- coding: utf-8 -*-

import json
import colorama
colorama.init()
from modules import coloring
coloring = coloring.coloring
from modules import logwrite


class Blocked():

	def __init__(self, proxies):
		self.proxies = proxies
		self.blacklist = []
		self.NAME = "\x1b[32m" + "[P-M]" + "\x1b[0m"
		with open("texts/blacklist.txt", mode="r") as file:
			self.blacklist = file.read().split("\n")
			while True:
				try:
					self.blacklist.remove("")
				except:
					break
			while True:
				try:
					self.blacklist.remove(" ")
				except:
					break

		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i].split(":")  # разделение по айпи и портам

	def start(self):

		self.proxies = Blocked.remove_blocked(self, self.proxies)
		
		for i in range(0, len(self.proxies)):
			try:
				self.proxies[i] = self.proxies[i][0] + ":" + self.proxies[i][1]
			except Exception as e:
				print(self.NAME + coloring("Непредвиденная ошибка: {0}".format(e), "red"))
				logwrite.log(e, "blocked", name="в соединение проксей")
			continue
		
		return self.proxies

	# def filtering_ips_1(self, proxylist):
	# 	output = []
	# 	for i in proxylist:
	# 		for j in output:
	# 			if i[0] == j[0]:
	# 				print(self.NAME + coloring("Найден повторяющийся айпи в прокси {0}, удаление...".format(i[0] + ":" + i[1]), "yellow"))
	# 				break
	# 			elif i == "":
	# 				break
	# 			else:
	# 				pass
	# 		else:
	# 			output.append(i)
	# 	return output

	def remove_blocked(self, proxylist):
		output = []
		for i in proxylist:
			for i2 in self.blacklist:
				if i[0] == i2:
					print(self.NAME + "Найдена прокси, находящийся в айпи-блеклисте {0}".format(i[0] + ":" + i[1]))
					break
				elif i == '':
					break
				else:
					pass
			else:
				output.append(i)
		return output

if __name__ == '__main__':
	pass