# -*- coding: utf-8 -*-


class Blocked():

	def __init__(self, proxies):
		self.proxies = proxies
		self.blacklist = []
		self.NAME = "\x1b[32m" + "[P-M]" + "\x1b[0m"
		with open("texts/blacklist.txt", mode="r") as file:
			self.blacklist = file.read().split("\n")
			for i in self.blacklist:
				if i == "" or i == " ":
					self.blacklist.remove(i)  # удаление пустых строк
		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i].split(":")  # разделение по айпи и портам

	def start(self):
		self.proxies = Blocked.filtering_ips(self, self.proxies)  # проверка на повторы
		self.proxies = Blocked.remove_blocked(self, self.proxies)
		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i][0] + ":" + self.proxies[i][1]
		
		return self.proxies

	def filtering_ips(self, lst):
		out = []  # выходной список
		for i in lst:  
			ifdouble = False  # флаг обнаруженного повтора
			for i2 in out:
				if i[0] == i2[0]:
					ifdouble = True
				elif ifdouble:
					break
				else:
					continue
			if not ifdouble:
				out.append(i)
			else:
				print(self.NAME + "Найден повторяющийся айпи в прокси {0}, удаление...".format(i[0] + ":" + i[1]))
		return out

	def remove_blocked(self, proxylist):
		output = []
		for i in proxylist:
			ifblocked = False
			for i2 in self.blacklist:
				if i[0] == i2:
					print(self.NAME + "Найдена прокси, находящийся в айпи-блеклисте {0}".format(i[0] + ":" + i[1]))
					ifblocked = True
					break
			if not ifblocked:
				output.append(i)
		return output