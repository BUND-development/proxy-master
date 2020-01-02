

import re
from modules import logwrite
from modules import coloring
coloring = coloring.coloring
import configparser
from colorama import init as init_ 
init_()
import progressbar


class Main(object):
	"""
	Удаление невалидных прокси и удаление одинаковых
	"""
	def __init__(self, proxylist, ifsame):
		super(Main, self).__init__()
		self.proxies = proxylist
		self.same = ifsame
		####################################
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		del config

	def check_for_valid(self, lst):
		'''
		Проверка на валидность
		'''
		lst2 = []
		output = []
		##############
		for i in lst:
			try:
				if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", i):  # если айпи подходит под шаблон
					lst2.append(i)
				else:
					print(self.NAME + "Найдена невалидная прокси {0}".format(i))
			except Exception as e:
				print(self.NAME + "Ошибка! Просьба отправить BUGREPORT на почту или отписаться в тред")
				logwrite.log(e, "removeshit", line=25)
		#################################
		for i in range(0, len(lst2)):
			lst2[i] = lst2[i].split(":")  # разделение на айпи и порт
			lst2[i][0] = lst2[i][0].split(".")
		###############################
		for i in lst2:
			for i2 in i[0]:
				if (int(i2) > 255 or int(i2) < 0) or (len(i2)>= 2 and (i2[0] == "0" or i2[0:2] == "00")):
					print(self.NAME + "Найден невалидный блок прокси {0}".format(i2))
					break
			else:
				output.append(i)
		###############################
		for i in range(0, len(output)):
			# i = [['77', '69', '23', '183'], '4145']
			ip = output[i][0][0] + '.' + output[i][0][1] + '.' + output[i][0][2] + '.' + output[i][0][3] + ":" + output[i][1]
			output[i] = ip
		###############
		return output

	def checksame(self, prlist):
		'''
		Удаление прокси с одинаковыми айпи
		'''
		print(self.NAME + coloring("Удаление прокси с одинаковыми IP...", "green"))
		output = []
		###################################
		prlist_len = len(prlist)
		dictOfproxies = {}
		pbar = progressbar.ProgressBar(maxval=prlist_len-1)
		pbar.start()
		for index in range(0, prlist_len):
			try:
				proxy = prlist[index].split(":")
			except Exception as e:
				logwrite.log(e, "removeshit", name="ошибка при разделении прокси")
				continue
			#####################
			dictOfproxies.update([proxy, ])
			pbar.update(index)
		###############################
		pbar.finish()
		#######################
		for i in dictOfproxies:
			output.append(i + ":" + dictOfproxies[i])
		#############
		return output

	def start(self):
		print(self.NAME + coloring("Удаление невалидных проксей...", "green"))
		try:
			self.proxies = self.check_for_valid(self.proxies)
		except KeyboardInterrupt:
			print(self.NAME + coloring("Чисткан невалидных проксей отменена!", "red"))
		except Exception as e:
			print(self.NAME + "Критическая ошибка модуля фильтрования невалидных прокси!")
			logwrite.log(e, "removeshit", name="сломалось в старте")
		#################
		if self.same:
			try:
				self.proxies = self.checksame(self.proxies)
			except KeyboardInterrupt:
				print(self.NAME + coloring("Удаление дублей отмненено!", "red"))
			except Exception as e:
				raise e
		print(self.NAME + coloring("Чистка проксей закончена.", "green"))
		return self.proxies



if __name__ == '__main__':
	pass
