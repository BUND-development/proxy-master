#!/usr/bin/python3
# -*- coding: utf-8 -*-



def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--default", dest="useDefault", default=0, type=bool, help="1 for use default config in \
		texts/settings.default.ini")  # use default config in texts/settings.default.ini
	parser.add_argument("-s", "--settings", dest="settingsFile", default="settings.ini", help="another configfile path")  # use configfile
	parser.add_argument("-o", "--output", dest="outputFile", default=None, help="output filename for good proxies")  # default output file with proxies
	parser.add_argument("-r", "--reinstall-packages", dest="reinstall", default=0, type=bool, help="1 for reinstall/upgrade pip packages")  # reinstall/upgrade pip packages
	parser.add_argument("-p", "--proxy", dest="proxy", default=None, help="proxy in format protocol://proxy:port")  # proxy using to parse web pages
	parser.add_argument("-i", "--input", dest="inputFile", default="input-proxies.txt", help="input file for proxies")  # default input file
	parser.add_argument("-pr", "--protocol", dest="protocol", default=None, help="default protocol of non-formated proxis")  # default protocol
	parser.add_argument("-if", "--ignore-formated", dest="ignore", default=0, type=bool, help="ignore formated proxies and use only input protocol")  # ignore formated proxies
	args = parser.parse_args(sys.argv[1:])
	return args

def main():
	tools.cls()
	tools.out_logo()

	args = parse_args()
	
	if args.useDefault:
		settingsFile = "texts/settings.default.ini"
	else:
		settingsFile = args.settingsFile

	config = configparser.ConfigParser()
	config.read(args.settingsFile, encoding="UTF-8")
	PARSE = config.getboolean("modules", "PARSE")
	SUBNETS = config.getboolean("modules", "SUBNETS")
	BLACKLIST = config.getboolean("modules", "BLACKLIST")
	USER_CHECK = config.getboolean("modules", "USER_CHECK")
	CHECKON2CH = config.getboolean("modules", "CHECKON2CH")
	CHECK_ADVANCED = config.getboolean("modules", "CHECK_ADVANCED")
	SAME_FILTERING = config.getboolean("modules", "SAME_FILTERING")
	CHECK2IP = config.getboolean("modules", "CHECK2IP")
	COUNTRIES = config.getboolean("modules", "COUNTRIES")
	CHECK2IP_CODES = config.getboolean("modules", "CHECK2IP_CODES")
	#CHECK_HEADERS = config.getboolean("modules", "CHECK_HEADERS")
	# will be soon...
	CHECK_HEADERS = False
	PROTOCOLOUT = config.getboolean("main", "PROTOCOLOUT")
	FILENAME_EXPORT = config["main"]["FILENAME_EXPORT"]
	NORMALINPUT = config.getboolean("main", "NORMALINPUT")
	FILTERINGBAD = config.getboolean("main", "FILTERINGBAD")
	NAME = "\x1b[32m" +  config["main"]["NAME"] + "\x1b[0m"
	########################
	#CHECKON2CH_TYPE = config["BANS_CHECKER"]["TYPE"]
	#CHECK_ADVANCED_TYPE = config["COUNTRIES_ADVANCED"]["TYPE"]
	del config
	
	

	if args.reinstall:
		tools.libInstaller()

	inputFile = args.inputFile

	if not args.protocol:
		protocol = input(colorama.Fore.GREEN + NAME + "Protocol> ")
	else:
		protocol = args.protocol

	if args.outputFile:
		FILENAME_EXPORT = args.outputFile
	

	proxies = []
	with open(inputFile, mode="r", encoding="UTF-8") as file:
		proxies_raw = file.read().split("\n")
		for i in proxies_raw:
			if i == "": continue
			try:
				proxies.append(tools.Proxy(i, protocol=protocol, ignoreFormated=args.ignore))
			except tools.ProxyInitError:
				print(f"{NAME}{colorama.Fore.YELLOW} Failed to init proxy {i}")
			except Exception as e:
				raise e

		print(colorama.Fore.YELLOW)
		print(NAME + colorama.Fore.GREEN + f"Default protocol {protocol}")
		
		if PARSE:
			start = proxy_parser.Parser(args.settingsFile)
			exported = [*start.main()]
			exported.extend(proxyscrape.start())
			for i in exported:
				try:
					proxies.append(tools.Proxy(i, protocol, ignoreFormated=args.ignore))
				except tools.ProxyInitError:
					print(f"{NAME}{colorama.Fore.YELLOW} Failed to init proxy {i}")
				except Exception as e:
					raise e

		if FILTERINGBAD:
			filtering = removeshit.Main(proxies, SAME_FILTERING, args.settingsFile)
			proxies = filtering.start()
		
		if BLACKLIST:
			filtering = blocked.Blocked(proxies, args.settingsFile)
			proxies = filtering.start()

		if SUBNETS:
			filtering = subnets_socket.FilteringSubnets(proxies, args.settingsFile)
			proxies = filtering.start()

		if CHECK2IP or CHECK2IP_CODES:
			filtering = countries_2ip.Countries2Ip(proxies, args.settingsFile)
			proxies = filtering.main()

		if COUNTRIES:
			proxies = weed.weed(proxies, args.settingsFile)

		if CHECK_ADVANCED:
			# if CHECK_ADVANCED_TYPE == "ASYNC":
			# 	filtering = countries_ipinfo.CheckerIpinfo(export, TYPE)
			# 	export = filtering.main()
			# else:
			# 	export = threading_countries_ipinfo.main(export, TYPE)
			filtering = countries_ipinfo.CheckerIpinfo(proxies, args.settingsFile)
			proxies = filtering.main()

		if CHECKON2CH:
			# if CHECKON2CH_TYPE == "ASYNC":
			# 	start = bans_checker.BansChecker(export, TYPE)
			# 	export = start.main()
			# else:
			# 	export = threading_bans_checker.main(export, TYPE)
			start = bans_checker.BansChecker(proxies, args.settingsFile)
			proxies = start.main()

		if CHECK_HEADERS:
			start = headers_check.HeadersChecker(proxies, args.settingsFile)
			export = start.main()

		if USER_CHECK:
			start = userlink_checker.UserChecker(proxies, args.settingsFile)
			proxies = start.main()

		print("", end="\n\n")
		print(NAME + f"Total {str(len(proxies))} proxies.")

		with open(FILENAME_EXPORT, mode="w", encoding="UTF-8") as file:
			for i in proxies:
				if PROTOCOLOUT:
					file.write(i.formated + "\n")
				else:
					file.write(i.normal + "\n")
	

	


if __name__ == '__main__':
	try:
		# from modules import proxyscrape, subnets_socket, blocked, weed, \
		# 	removeshit, headers_check, bans_checker, userlink_checker, proxy_parser, \
		# 	countries_2ip, countries_ipinfo, threading_bans_checker, \
		# 	threading_countries_ipinfo
		from modules import tools, proxyscrape, proxy_parser, removeshit, blocked, subnets_socket, \
		countries_2ip, weed, countries_ipinfo, bans_checker, headers_check, userlink_checker
		import argparse
		import sys
		import configparser
		import colorama
		colorama.init(autoreset=True)
	except Exception as e:
		print(f"Error while importing modules: {e}", end="\n\n\n")
		raise e
	else:
		print(colorama.Fore.GREEN + "All modules was loaded successfully!")
	
	main()
