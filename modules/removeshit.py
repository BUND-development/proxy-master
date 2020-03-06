

import re
from modules import tools
import configparser
import colorama
colorama.init(autoreset=True)
import progressbar


class Main(object):
	"""
	Удаление невалидных прокси и удаление одинаковых
	"""
	def __init__(self, proxylist, ifsame, settings):
		super(Main, self).__init__()
		self.proxies = proxylist
		self.same = ifsame
		####################################
		config = configparser.ConfigParser()
		config.read(settings, encoding="UTF-8")
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
				if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", i.normal):  # если айпи подходит под шаблон
					lst2.append(i)
				else:
					print(self.NAME + f"Found invalid proxy: {i}")
			except Exception as e:
				print(self.NAME + f"Critical error {e}, send BUGREPORT file.")
				tools.log(e, "removeshit", line=25)
				raise e
		#################################
		for i in lst2:
			for i2 in i.octets:
				if (int(i2) > 255 or int(i2) < 0) or (len(i2)>= 2 and (i2[0] == "0" or i2[0:2] == "00")):
					print(self.NAME + f"Found invalid proxy octet: {i2}")
					break
			else:
				output.append(i)
		###############
		return output

	def checksame(self, prlist):
		'''
		Удаление прокси с одинаковыми айпи
		'''
		print(self.NAME + colorama.Fore.GREEN + "Deleting proxies with same hosts...")
		output = []
		###################################
		prlist_len = len(prlist)
		dictOfproxies = {}
		pbar = progressbar.ProgressBar(maxval=prlist_len-1)
		pbar.start()
		for index in range(0, prlist_len):
			dictOfproxies.update([[prlist[index].host, prlist[index]], ])
			pbar.update(index)
		###############################
		pbar.finish()
		#######################
		for i in dictOfproxies:
			output.append(dictOfproxies[i])
		#############
		return output

	def start(self):
		print(self.NAME + colorama.Fore.GREEN + "Deleting invalid proxies...")
		try:
			self.proxies = self.check_for_valid(self.proxies)
		except KeyboardInterrupt:
			print(self.NAME + colorama.Fore.RED + "Deleting invalid proxies cancelled!")
		except Exception as e:
			print(self.NAME + f"Critical error {e}, send BUGREPORT file.")
			tools.log(e, "removeshit", name="сломалось в старте")
			raise e
		#################
		if self.same:
			try:
				self.proxies = self.checksame(self.proxies)
			except KeyboardInterrupt:
				print(self.NAME + colorama.Fore.RED + "Deleting proxies with same hosts cancelled!")
			except Exception as e:
				raise e
		print(self.NAME + colorama.Fore.GREEN + "Clearing proxies finished!")
		return self.proxies



if __name__ == '__main__':
	pass
