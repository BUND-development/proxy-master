# -*- coding: utf-8 -*-

import json
import colorama
colorama.init()


def coloring(string, color):
	'''Мой мини-модуль для раскрашивания текста'''
	if color == "red":
		string = "\x1b[31m" + string + "\x1b[0m"
	elif color == "green":
		string = "\x1b[32m" + string + "\x1b[0m"
	elif color == "yellow":
		string = "\x1b[33m" + string + "\x1b[0m"
	elif color == "blue":
		string = "\x1b[34m" + string + "\x1b[0m"
	else:
		pass
	#string = "\x1b[32m[P-M] \x1b[0m" + string
	return string


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
		with open("settings.ini", mode="r") as file:
			settings = json.load(file)
			self.THREADS_MULTIPLIER = settings["THREADS_MULTIPLIER"]

		for i in range(0, len(self.proxies)):
			self.proxies[i] = self.proxies[i].split(":")  # разделение по айпи и портам

	def start(self):
		try:
			self.proxies = Blocked.filtering_ips_1(self, self.proxies)
		except KeyboardInterrupt:
			print(self.NAME + coloring("Принудительный выход...", "red"))
		except Exception as e:
			print("Непредвиденная ошибка: {0}".format(e))
			with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
				file.write("=====================\n{0}\n".format(str(e)))
		else:
			pass

		self.proxies = Blocked.remove_blocked(self, self.proxies)
		
		for i in range(0, len(self.proxies)):
			try:
				self.proxies[i] = self.proxies[i][0] + ":" + self.proxies[i][1]
			except Exception as e:
				print(self.NAME + coloring("Непредвиденная ошибка: {0}".format(e), "red"))
				with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
					file.write("=====================\n{0}\n proxy: {1}\n".format(str(e), str(self.proxies[i])))
			continue
		
		return self.proxies

	def filtering_ips_1(self, proxylist):
		output = []
		for i in proxylist:
			for j in output:
				if i[0] == j[0]:
					print(self.NAME + coloring("Найден повторяющийся айпи в прокси {0}, удаление...".format(i[0] + ":" + i[1]), "yellow"))
					break
				elif i == "":
					break
				else:
					pass
			else:
				output.append(i)
		return output


	def filtering_ips(self, lst, output):
		'''Удаление повторяющихся айпи '''
		while len(lst):
			try:
				i = lst.pop()
			except KeyboardInterrupt:
				print(self.NAME + "Принудительный выход...")
				break
			except IndexError:
				print(self.NAME + "0 проксей в общем списке, выход из потока...")
				break
			except Exception as e:
				print("[{0} проксей осталось] ".format(str(len(lst))), end="")
				print("Непредвиденная ошибка: {0}".format(e))
				with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
					file.write("=====================\n{0}\n".format(str(e)))
			else:
				for j in output:
					if i[0] == j[0]:  
						print(coloring("[{0} проксей осталось] ".format(str(len(lst))), "green"), end="")
						print(coloring("Найден повторяющийся айпи в прокси {0}, удаление...".format(i[0] + ":" + i[1]), "yellow"))
						break
					if i == "":  # заодно добавил фильтр на мусор
						break
				else:
					output.append(i)

				#print(self.NAME + "Найден повторяющийся айпи в прокси {0}, удаление...".format(i[0] + ":" + i[1]))

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