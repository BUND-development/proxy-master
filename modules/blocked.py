# -*- coding: utf-8 -*-



import colorama
colorama.init(autoreset=True)
import configparser



class Blocked():
	'''
	Удаление проксей из блеклиста
	'''
	def __init__(self, proxies, settings):
		self.proxies = proxies
		self.blacklist = []
		config = configparser.ConfigParser()
		config.read(settings, encoding="UTF-8")
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

	def start(self):
		print(self.NAME + colorama.Fore.GREEN + "Started removing blacklist hosts...")
		self.proxies = self.remove_blocked(self.proxies)
		####################################
		print(self.NAME + colorama.Fore.GREEN + "Finishied removing blacklist hosts...")
		return self.proxies

	def remove_blocked(self, proxylist):
		output = []
		for i in proxylist:
			for i2 in self.blacklist:
				if i.host == i2 or i.host == '':
					print(self.NAME + colorama.Fore.YELLOW + f"Found proxy with blacklist host {i.normal}")
					break
			else:
				output.append(i)
		return output



if __name__ == '__main__':
	pass