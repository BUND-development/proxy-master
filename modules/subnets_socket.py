# -*- coding: utf-8 -*-



import socket,struct
import ipaddress
from modules import tools
import configparser
import re
import colorama
colorama.init(autoreset=True)


class FilteringSubnets():
	''' Some of code was taiken from: http://qaru.site/questions/76775/how-can-i-check-if-an-ip-is-in-a-network-in-python'''
	def __init__(self, proxies, settings):
		self.proxies = list(proxies)
		self.subnets = []
		###################################
		config = configparser.ConfigParser()
		config.read(settings, encoding="UTF-8")
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

	def start(self):
		print(self.NAME + colorama.Fore.GREEN + "Started filtering subnets...")
		#####################################################################
		try:
			if self.MODE == "EXCEPT":
				self.proxies = self.addressInNetwork(self.proxies)
			elif self.MODE == "INCLUDE":
				self.proxies = self.addressOutNetwork(self.proxies)
			else:
				print(self.NAME + colorama.Fore.RED + f"INVALID SETTING: {self.MODE}")
				input(self.NAME + "Press any key to skip filtering...")
		except KeyboardInterrupt:
			print(self.NAME + colorama.Fore.GREEN + "Cancelled!")
		######################################
		print(self.NAME + colorama.Fore.GREEN + "Finished filtering subnets...")
		###################
		return self.proxies

	def addressInNetwork(self, proxylist):
		output = []
		for i in range(0, len(proxylist)):
			for subnet in self.subnets:
				try:
					if ipaddress.ip_address(proxylist[i].host) in ipaddress.ip_network(subnet):
						print(self.NAME + colorama.Fore.YELLOW + f"Removed host in blacklist subnet: {proxylist[i].host}")
						break
					else:
						pass
				except ValueError:
					print(self.NAME + f"Removed invalid host: {proxylist[i].host}")
					break
				except Exception as e:
					print(self.NAME + f"Error: {e}")
					tools.log(e, "sunets", name="ошибка в проверке адреса")
					raise e
					break
			else:
				output.append(proxylist[i])
		return output

	def addressOutNetwork(self, proxylist):
		output = []
		for i in range(0, len(proxylist)):
			for subnet in self.subnets:
				try:
					if ipaddress.ip_address(proxylist[i].host) in ipaddress.ip_network(subnet):
						break
					else:
						pass
				except ValueError:
					continue
				except Exception as e:
					print(self.NAME + f"Error: {e}")
					tools.log(e, "sunets", name="ошибка в проверке адреса")
					raise e
					break
			else:
				print(self.NAME + colorama.Fore.GREEN + f"Removed host in non-whitelist subnet: {proxylist[i].host}")
				continue
			###########################
			output.append(proxylist[i])
		return output



if __name__ == '__main__':
	pass
