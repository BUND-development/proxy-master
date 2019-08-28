# -*- coding: utf-8 -*-
import requests 



class ProxyScrape():

	def __init__(self):
		self.proxylist = []
		self.apiurl = "https://api.proxyscrape.com"
		self.modulename = "ProxyScrape"
		self.parametrs = {
		"request": "getproxies"
		}
		#self.NAME = "\x1b[32m" + "[P-M]" + "\x1b[0m"


	def start(self):
		answer = requests.get(self.apiurl, params=self.parametrs, timeout=30)
		answer = answer.text
		answer = answer.split("\r\n")
		try:
			answer.remove("")
		except:
			pass
		return answer


if __name__ == '__main__':
	starting = ProxyScrape()
	print(starting.start())