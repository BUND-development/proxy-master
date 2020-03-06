# -*- coding: utf-8 -*-

import sys
import re
import pygeoip
import configparser
import colorama
colorama.init(autoreset=True)


def get_states(filename):
	states = []
	with open(filename,"r") as file:
		for state in file:
			state = state[0:-1]
			states.append(str(state))
	states.sort()
	return states

def weed(proxies, settings):
	''' Code by LOH2.0'''
	config = configparser.ConfigParser()
	config.read(settings, encoding="UTF-8")
	NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
	del config
	print(NAME + colorama.Fore.GREEN + "Stared filtering countries...")
	########################################
	states = get_states("texts/countries.txt")
	gi = pygeoip.GeoIP("texts/GeoIP.dat")
	export = []
	for i in proxies:
		try:
			state = str(gi.country_name_by_addr(i.host))
		except Exception as e:
			raise e
		###################################
		if (state == "None"):
			export.append(i)
		elif not (state in states):
			export.append(i)
		else:
			print(NAME + f"Found ip from blacklist country: {i.normal}")
	print(NAME + colorama.Fore.GREEN + f"Finished filtering countries, {str(len(export))} good proxies.")
	return export



if __name__ == '__main__':
	pass
