# -*- coding: utf-8 -*-



import socket,struct
import ipaddress
from modules import logwrite
import configparser
import re
from modules import coloring
coloring = coloring.coloring


class FilteringSubnets():
	''' Алгоритм и часть кода взята отсюда: http://qaru.site/questions/76775/how-can-i-check-if-an-ip-is-in-a-network-in-python'''
	def __init__(self, proxies):
		self.proxies = list(proxies)
		self.subnets = []
		###################################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		self.MODE = config["SUBNETS"]["MODE"]
		del config
		####################################
		with open("texts/subnets.txt", mode="r") as file:
			self.subnets = file.read().split("\n")
			while True:
				try:
					self.subnets.remove("")
				except:
					break
		print(self.NAME + "Фильтрование подсетей...")

	def start(self):
		print(self.NAME + coloring("Фильтрация подсетей начата...", "green"))
		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i].split(":")  # разделение на айпи и порт
		#####################################################################
		if self.MODE == "EXCEPT":
			self.proxies = self.addressInNetwork(self.proxies)
		elif self.MODE == "INCLUDE":
			self.proxies = self.addressOutNetwork(self.proxies)
		else:
			print(self.NAME + coloring("Невалидные настройки в SUBNETS!", "red"))
			input(self.NAME + "Нажмите любую клавишу для пропуска модуля")
			return self.proxies
		######################################
		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i][0] + ":" + self.proxies[i][1]  # соединение айпи и порта
		print(self.NAME + coloring("Фильтрация подсетей закончена.", "green"))
		###################
		return self.proxies

	def addressInNetwork(self, proxylist):
		output = []
		for i in range(0, len(proxylist)):
			for subnet in self.subnets:
				try:
					if ipaddress.ip_address(proxylist[i][0]) in ipaddress.ip_network(subnet):  # входит ли айпи в запрещенную подсеть
						print(self.NAME + "Удален айпи ({0}), входящий в запрещенную подсеть.".format(str(proxylist[i][0])))
						break
					else:
						pass
				except ValueError:
					print(self.NAME + "Удален невалидный айпи ({0})".format(i[0]))
					break
				except Exception as e:
					print(self.NAME + "Необработанная ошибка!")
					logwrite.log(e, "sunets", name="ошибка в проверке адреса")
					break
			else:
				output.append(proxylist[i])
		return output

	def addressOutNetwork(self, proxylist):
		output = []
		for i in range(0, len(proxylist)):
			for subnet in self.subnets:
				try:
					if ipaddress.ip_address(proxylist[i][0]) in ipaddress.ip_network(subnet):  # входит ли айпи в подсеть
						break
					else:
						pass
				except ValueError:
					continue
				except Exception as e:
					print(self.NAME + "Необработанная ошибка!")
					logwrite.log(e, "sunets", name="ошибка в проверке адреса")
					break
			else:
				print(self.NAME + "Удален айпи ({0}), не входящий в разрешенную подсеть.".format(str(proxylist[i][0])))
				continue
			###########################
			output.append(proxylist[i])
		return output



if __name__ == '__main__':
	pass
