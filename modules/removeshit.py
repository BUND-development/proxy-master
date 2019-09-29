

import re
from modules import logwrite
from modules import coloring
coloring = coloring.coloring
import configparser
from colorama import init as init_ 
init_()

class Main(object):
	"""docstring for Main"""
	def __init__(self, proxylist, ifsame):
		super(Main, self).__init__()
		self.proxies = proxylist
		self.same = ifsame

		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		del config

	def check_for_valid(self, lst):
		lst2 = []
		output = []
		for i in lst:
			try:
				if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", i):  # если айпи подходит под шаблон
					lst2.append(i)
				else:
					print(self.NAME + "Найдена невалидная прокси {0}".format(i))
			except Exception as e:
				print(self.NAME + "Ошибка! Просьба отправить BUGREPORT на почту или отписаться в тред")
				logwrite.log(e, "removeshit", line=25)
			
		for i in range(0, len(lst2)):
			lst2[i] = lst2[i].split(":")  # разделение на айпи и порт
			lst2[i][0] = lst2[i][0].split(".")
			
		for i in lst2:
			for i2 in i[0]:
				if (int(i2) > 255 or int(i2) < 0) or (len(i2)>= 2 and (i2[0] == "0" or i2[0:2] == "00")):
					print(self.NAME + "Найден невалидный блок прокси {0}".format(i2))
					break
			else:
				output.append(i)
			
		for i in range(0, len(output)):
			# i = [['77', '69', '23', '183'], '4145']
			ip = output[i][0][0] + '.' + output[i][0][1] + '.' + output[i][0][2] + '.' + output[i][0][3] + ":" + output[i][1]
			output[i] = ip

		return output

	def checksame(self, prlist):
		output = []
		for index in range(0, len(prlist)):
			try:
				proxy = prlist[index].split(":")
			except Exception as e:
				logwrite.log(e, "removeshit", name="ошибка при разделении прокси")
				continue
			else:
				for proxy_out in output:
					if proxy_out[0] == proxy[0]:
						print(self.NAME + coloring("Найдена прокси с уже имеющимся айпи: {0}".format(proxy[0] + ":" + proxy[1]), "yellow"))
						break
				else:
					output.append(proxy)
		for i in range(0, len(output)):
			output[i] = output[i][0] + ":" + output[i][1]
		return output

	def start(self):
		try:
			self.proxies = self.check_for_valid(self.proxies)
			if self.same:
				self.proxies = self.checksame(self.proxies)
		except Exception as e:
			print(self.NAME + "Критическая ошибка модуля фильтрования невалидных прокси!")
			logwrite.log(e, "removeshit", name="сломалось в старте")
		return self.proxies


		

if __name__ == '__main__':
	pass