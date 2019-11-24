# -*- coding: utf-8 -*-

import sys
import re
import pygeoip
import configparser
from modules import coloring
coloring = coloring.coloring


def get_states(filename):
	states = []
	with open(filename,"r") as file:
		for state in file:
			state = state[0:-1]
			states.append(str(state))
	states.sort()
	return states

def weed(IPs):
	''' Модуль взят и модифицирован у LOH2.0'''
	config = configparser.ConfigParser()
	config.read("settings.ini", encoding="UTF-8")
	NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
	del config
	print(NAME + coloring("Фильтрация по странам началась...", "green"))
	########################################
	states = get_states("texts/countries.txt")
	gi = pygeoip.GeoIP("texts/GeoIP.dat")
	export = []
	for IP in IPs:
		try:
			IP = re.sub("\n", '', IP)
			pos = IP.find("/")
			addr = IP[pos+2:len(IP)] if (pos != -1) else IP
			pos = addr.find(":")
			###################################
			if (pos != -1): addr = addr[0:pos]
			state = str(gi.country_name_by_addr(addr))
			###################################
			if (state == "None"):
				export.append(IP)
			elif not (state in states):
				export.append(IP)
			else:
				print(NAME + f"Найден айпи из блек-лист страны {IP}")
		except Exception:
			pass
	print(NAME + coloring("Фильтрация по странам закончена.", "green"))
	return export



if __name__ == '__main__':
	IPs = get_IPs(sys.argv[1])  # айпи
	states = get_states(sys.argv[2])  # страны
	output = sys.argv[3]  # выходной файл
	flag = int(sys.argv[4])  # 0 или 1, если 1 чистятся не найденные айпишники
	weed(IPs)
	print("All right!")
