# -*- coding: utf-8 -*-
import requests 
import urllib3



class ProxyScrape():

	def __init__(self):
		self.proxylist = []
		self.apiurl = "https://api.proxyscrape.com"
		self.modulename = "ProxyScrape"
		self.parametrs = {
		"request": "getproxies"
		}


	def start(self):
		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		answer = requests.get(self.apiurl, params=self.parametrs, timeout=30, verify=False)
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
