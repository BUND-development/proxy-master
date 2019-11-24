# -*- coding: utf-8 -*-


import requests 
from urllib3 import disable_warnings, exceptions



def start():
	proxylist = []
	apiurl = "https://api.proxyscrape.com"
	modulename = "ProxyScrape"
	parametrs = {
	"request": "getproxies"
	}
	disable_warnings(exceptions.InsecureRequestWarning)
	try:
		answer = requests.get(apiurl, params=parametrs, timeout=30, verify=False)
	except:
		return None
	answer = answer.text
	answer = answer.split("\r\n")
	while True:
		try:
			answer.remove("")
		except:
			break
	return answer



if __name__ == '__main__':
	pass
