# -*- coding: utf-8 -*-

import socket,struct
import ipaddress
import re

class FilteringSubnets():
	''' Алгоритм и часть кода взята отсюда: http://qaru.site/questions/76775/how-can-i-check-if-an-ip-is-in-a-network-in-python'''

	def __init__(self, proxies):
		self.proxies = list(proxies)
		self.subnets = []
		self.NAME = "\x1b[32m" + "[P-M]" + "\x1b[0m"
		with open("texts/subnets.txt", mode="r") as file:
			self.subnets = file.read().split("\n")
			for i in self.subnets:
				if (i == "") or (i == " ") or ("#" in i):  # удаление комментариев и пустых строк
					self.subnets.remove(i)
		print(self.NAME + "Фильтрование подсетей...")

	def start(self):
		# проверка на валидность прокси
		self.proxies = FilteringSubnets.check_for_valid(self, self.proxies)  # удаление невалидных прокси
		# дальше баги
		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i].split(":")  # разделение на айпи и порт

		
		self.proxies = FilteringSubnets.addressInNetwork(self, self.proxies)  # удаление айпи, входящих в запрещенные подсети
		
		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i][0] + ":" + self.proxies[i][1]  # воссоединение айпи
		
		return self.proxies

	def check_for_valid(self, lst):
		# r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
		lst2 = []
		output = []
		for i in lst:
			try:
				if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", str(i)):  # если айпи подходит под шаблон
					lst2.append(str(i))
				else:
					print(self.NAME + "Найдена невалидная прокси {0}".format(i))
			except Exception as e:
				print(self.NAME + "Ошибка! Просьба отправить BUGREPORT на почту или отписаться в тред")
				with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
					file.write("\n====================\n {0} \n proxy: {1}".format(e, str(i)))
			
		for i in range(0, len(lst2)):
			lst2[i] = lst2[i].split(":")  # разделение на айпи и порт
			lst2[i][0] = lst2[i][0].split(".")
			
		for i in lst2:
			valid = True
			for i2 in i[0]:
				if (int(i2) > 255 or int(i2) < 0) or (len(i2)>= 2 and (i2[0] == "0" or i2[0:2] == "00")):
					valid = False
					print(self.NAME + "Найден невалидный блок прокси {0}".format(i2))
					break
			if valid:
				output.append(i)
			
		for i in range(0, len(output)):
			# i = [['77', '69', '23', '183'], '4145']
			ip = output[i][0][0] + '.' + output[i][0][1] + '.' + output[i][0][2] + '.' + output[i][0][3] + ":" + output[i][1]
			output[i] = ip

		return output

	def addressInNetwork(self, proxylist):
		output = []
		for i in range(0, len(proxylist)):
			ifinsubnet = False
			for subnet in self.subnets:
				try:
					if ipaddress.ip_address(proxylist[i][0]) in ipaddress.ip_network(subnet):  # входит ли айпи в запрещенную подсеть
						print(self.NAME + "Удален айпи ({0}), входящий в запрещенную подсеть.".format(str(proxylist[i][0])))
						ifinsubnet = True
						break
					else:
						pass
				except ValueError:
					print(self.NAME + "Удален невалидный айпи ({0})".format(i[0]))
				except:
					input(self.NAME + "Необработанная ошибка!")
					print(proxylist[i])
				else:
					pass
			if not ifinsubnet:
				output.append(proxylist[i])

		return output
			


if __name__ == '__main__':
	start = FilteringSubnets(['103.79.169.153:4145', '54.38.81.12:45907', '127.0.0.1:228'])
	print(start.start())