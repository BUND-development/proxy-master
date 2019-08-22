# -*- coding: utf-8 -*-

import socket,struct
import ipaddress
import re

class FilteringSubnets():
	''' Алгоритм и часть кода взята отсюда: http://qaru.site/questions/76775/how-can-i-check-if-an-ip-is-in-a-network-in-python'''

	def __init__(self, proxies):
		self.proxies = proxies
		self.subnets = []
		with open("subnets", mode="r") as file:
			self.subnets = file.read().split("\n")
			for i in self.subnets:
				if (i == "") or (i == " ") or ("#" in i):  # удаление комментариев и пустых строк
					self.subnets.remove(i)
		print("Фильтрование подсетей...")

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
		# дальше баги
		for i in lst:
			if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", i):  # если айпи подходит под шаблон
				lst2.append(i)
			else:
				print("Найдена невалидная прокси {0}".format(i))
			
		for i in range(0, len(lst2)):
			lst2[i] = lst2[i].split(":")  # разделение на айпи и порт
			lst2[i][0] = lst2[i][0].split(".")
			
		for i in lst2:
			valid = True
			for i2 in i[0]:
				if int(i2) > 255 or int(i2) < 0:
					valid = False
					print("Найден невалидный блок прокси {0}".format(i2))
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
						print("Удален айпи ({0}), входящий в запрещенную подсеть.".format(str(proxylist[i][0])))
						ifinsubnet = True
						break
					else:
						pass
				except ValueError:
					print("Удален невалидный айпи ({0})".format(i[0]))
				except:
					input("Необработанная ошибка!")
					print(proxylist[i])
				else:
					pass
			if not ifinsubnet:
				output.append(proxylist[i])

		return output
			


if __name__ == '__main__':
	start = FilteringSubnets(['103.79.169.153:4145', '54.38.81.12:45907', '127.0.0.1:228'])
	print(start.start())