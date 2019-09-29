# -*- coding: utf-8 -*-

import os  # Работа с системой
def cls():
	'''Очистка консоли'''
	os.system('cls' if os.name=='nt' else 'clear')
# ============================================================
try:
	import json
	import requests
	import bs4
	import urllib3
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # отключение уведомлений об незащищенности соединения
	
	# модули
	from modules import logwrite
	from modules import coloring, logwrite
	coloring = coloring.coloring
	
	# многопоток
	from multiprocessing import Process, Lock, Manager
	
	# цвета в консоли
	import colorama  # цветной текст
	colorama.init()  # инициация в консоли цветного текста
	
	# остальное
	import configparser
	import re  # регулярные исключения
	import zipfile  # работа с архивами
	import random  # случайные числа
	import sys  # работа с системой

except:
	print(coloring("Ошибка импортирования модулей!", "red"))
	exit(1)
else:
	print(coloring("Модули ипортированы успешно!", "green"))



class Parsing():
	''' Класс парсинга прокснй и архивов с проксями'''
	def __init__(self):
		#super().__init__()
		self.MAINURLS = (  # сайты, с которых парсится основная часть проксей путем регулярных исключений и архивов
			"http://www.proxyserverlist24.top/",
			"http://www.socks24.org",
			"http://www.vipsocks24.net/",
			"http://www.socksproxylist24.top/",
			"http://www.sslproxies24.top/"
			)
		self.download_files = []  # список имен zip файлов, которые были скачаны 
		
		config = configparser.ConfigParser()
		config.read("settings.ini", encoding="UTF-8")
		self.PARSE_THREADS = config.getint("PARSER", "THREADS")
		self.TIMEOUT = config.getint("PARSER", "TIMEOUT")
		self.DOWNLOADTIMEOUT = config.getint("PARSER", "DOWNLOADTIMEOUT")
		self.NAME = "\x1b[32m" + config["main"]["NAME"] + "\x1b[0m"
		del config
		
# ============================================================
	# получение всех ссылок со страницы
	def get_links(self, url):
		try:
			results = requests.get(url, timeout=25, verify=False)  # поулчение страницы
		except Exception as e:
			print(self.NAME + coloring("Ошибка подключения! Проверьте соединение с сетью!", "red"))
			logwrite.log(e, "parser", name="getlinks")
		results = bs4.BeautifulSoup(results.text, "lxml")  # создание объекта супа из html страницы
		results = results.find_all('a')  # получения списка всех ссылок
		links = []  # список самих ссылок
		for i in results:
			link = i.get("href")  # получение самой ссылки из тега ссылки <a.....
			if link and ("#" not in link):
				links.append(link)
			else:
				pass
		random.shuffle(links)
		links = set(links)  # очистка дубликатов ссылок
		return links  # возвращение списка

# ============================================================
	# анализирование найденных юрлов
	def analizing_urls(self, lst, lstOfProxies):
		while len(lst):  # проходимся по всем найденным ссылкам
			try:
				url_name = lst.pop()  # получения ссылки из общего пула
			except IndexError:
				print(self.NAME + coloring("Конец потока...", "green"))
				break
			# ===================
			try:
				answer = requests.get(url_name, timeout=self.TIMEOUT, verify=False)  # получения страницы этой ссылки
			except KeyboardInterrupt:
				print(self.NAME + coloring("Принудительный выход...", "yellow"))
				break
			except:
				print(self.NAME + coloring("Не удалось получить страницу юрла.", "yellow"))
				continue
			else:
				print(self.NAME + coloring("Страница успешно скачана, проверяется наличие проксей...", ""))
			# ===================
			answer = bs4.BeautifulSoup(answer.text, "lxml")  # создание объекта супа из html страницы
			proxies_find = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", str(answer))  # поиск проксей на страницах с помощью регулярных выражений и добавление их в архив
			answer = answer.find_all("a")  # получение всех тегов ссылок
			# ===================
			for i in answer:
				# ===================
				link = i.get("href")  # получение самих ссылок
				# ===================
				try:
					if "zip" in link:  # если в ссылке есть слово zip
						# ===================
						print(self.NAME + coloring("Обнаружена ссылка на скачивание> {0}".format(str(link)), ""))
						# ===================
						link_in = requests.get(link, timeout=self.TIMEOUT, verify=False)  # получения страницы с файлом
						link_in = bs4.BeautifulSoup(link_in.text, "lxml")  # создание объекта супа этой страницы
						link_in = link_in.find_all("a")  # поиск всех тегов ссылок
						link_in = set(link_in)  # удаление дубликатов
						# ===================
						for download in link_in:
							try:
								# ===================
								download = download.get("href")  # получение ссылки
								# ===================
								if (".zip" in download):  # если есть четкая ссылка на .zip файл
									print(self.NAME + coloring("Обнаружена прямая ссылка на скачивание> {0}".format(str(download)), "green"))
									print(self.NAME + coloring("Скачивание файла...", ""))
									# ===================
									try:
										file = requests.get(download, timeout=self.DOWNLOADTIMEOUT)
									except Exception as e:
										print(self.NAME + coloring("Ошибка загрузки файла!", "red"))
										logwrite.log(e, "parser", link=str(download))
									else:
										print(self.NAME + coloring("Файл успешно загружен в память, идет запись на диск...", ""))
									# ===================
									filename = os.getcwd() + "/downloads/" + str(random.randint(1, 1000)) + ".zip"  # загрузка архива в папку 
									# ===================
									with open(filename, mode="wb") as zipfile:  # запись архива в файл
										zipfile.write(file.content)  # запись zip файла
										# ===================
										print(self.NAME + 
											coloring(
												"Обнаруженный архив загружен успешно и сохранен: {0}".format(filename),
												"green"
												)
											)
										# ===================
							except:
								pass
				# ===================
				except:
					pass
			# ==============================================
			if len(proxies_find) != 0:  # если нашлись прокси
				print(self.NAME + 
					coloring(
						"Найдено {0} проксей, ".format(len(proxies_find)), 
						""
						), 
					end=""
					)
				# ===================
				proxies_find = set(proxies_find)  # очистка от дублей
				# ===================
				print(
					coloring(
						"из них {0} уникальные.".format(len(proxies_find)),
						"green"
						)
					)
				# ===================			
				lstOfProxies.extend(proxies_find)  # добавление списка проксей к уже имеющимся прокси
			else:
				print(self.NAME + coloring("Не найдено проксей на скачанной странице.", "yellow"))
		

# ============================================================
	def parsing(self):
		'''Получение проксей из различных источников'''
		proxies = []
		list_p = []  # список напарсенных ссылок
		# ===================
		try:
			os.mkdir("downloads")  # создание директории для временного хранения скачанных архивов
		except:
			pass
		# ===================
		for url in self.MAINURLS:
			try:
				list_p.extend(Parsing.get_links(self, url))  # получение ссылок
			except Exception as e:
				print(self.NAME + coloring("Ошибка подключения! Проверьте соединение с сетью!", "red"))
				logwrite.log(e, "parser", name="ошибка подключения")
		# ===================
		#proxies.extend(Parsing.analizing_urls(self, list_p))  # получение списка проксей
		try:
			with Manager() as manager:
				lstOfProxies = manager.list(proxies)  # создание списка проксей между потоками
				lst = manager.list(list_p)  # тоже самое, но только со списком юрлов
				procs = []
				for i in range(0, self.PARSE_THREADS):
					proc = Process(target=Parsing.analizing_urls, args=(self, lst, lstOfProxies))
					proc.start()
					procs.append(proc)

				for pr in procs:
					# присоединение потока к осовному
					pr.join()
				print(self.NAME + coloring("Парсинг проксей с ссылок закончен.", "green"))
				proxies.extend(lstOfProxies)

		except Exception as e:
			print(self.NAME + coloring("Критическая ошибка модуля анализа юрлов!", "red"))
			logwrite.log(e, "parser", name="многопоток обосрался")
		# ===================
		proxies.extend(Parsing.open_archives(self))  # добавление архивов проксями к результату
		# ===================
		print(self.NAME + coloring("Итоговое количество проксей {0}, ".format(len(proxies)),""),
			end=""
			)
		proxies = set(proxies)
		print(coloring("из которых {0} уникальные.".format(len(proxies)),"green"))
		return proxies

# ============================================================
	def open_archives(self):
		'''Открытие и обработка архивов'''
		
		os.chdir("downloads")  # переход в папку downloads
		proxy_list = []
		badtryes = 0
		# ===================
		for i in os.listdir():
			if '.zip' in i:
				try:
					xfile = zipfile.ZipFile(i)  # создание переменной архива
					xfile.extractall()  # распаковка
					xfile.close()  # закрытие архива
					for i2 in os.listdir():  
						try:
							if '.txt' in i2:
								with open(i2, mode="r", encoding="utf-8") as txtfile:  # открытие Txt файла с проксями
									read = txtfile.read()  # прочтение содержимого файла
									read = read.split('\n')  # разделение содержимого по новой строке
									try:
										read.remove("")  # удаление строки с пустым символом если есть
									except:
										pass
									proxy_list.extend(read)  # добавление к уже имеющимся
									os.remove(i2)  # удаление txt
									os.remove(i)  # удаление архива
							else:
								continue
						except:
							print(self.NAME + coloring("Не удалось обработать файл {0}, но распаковка прошла успешно.".format(i2),
								"yellow"))
							continue
						else:
							print(self.NAME + coloring("Удалось успешно прочесть .txt файл! \n Получено {0} проксей.".format(len(proxy_list)),
									"green"))
							for i in os.listdir():
								if ".zip" in i:
									continue
								else:
									try:
										os.remove(i)
									except:
										print(self.NAME + coloring("Ошибка очистки каталога загрузок!", "red"))
										input(self.NAME + "Удалите все не .zip файлы и нажмите энтер...")
				except:
					print(self.NAME + coloring("Не удалось распаковать загруженный архив: {0}".format(i),
								"red"))
					badtryes += 1
					for i in os.listdir():
						if ".zip" in i:
							continue
						else:
							try:
								os.remove(i)
							except:
								print(self.NAME + coloring("Ошибка очистки каталога загрузок downloads!", "red"))
								input(self.NAME + "Удалите все не .zip файлы и нажмите энтер...")
		
		print(self.NAME + coloring("Удалось успешно распаковать скачанные архивы!\n" + self.NAME + "Получено {0} проксей, из них ".format(len(proxy_list)),
					""),end="")
		proxy_list = set(proxy_list)  # очистка от дублей
		print(coloring("{0} уникальные.".format(len(proxy_list)),"green"))
		print(badtryes * (self.NAME + coloring("Не удалось распаковать или обработать {0} архивов.".format(str(badtryes)),
				"red")),end= bool(badtryes) * "\n")

		for i in os.listdir():
			try:
				os.remove(i)
			except:
				print(self.NAME + coloring("Ошибка очистки каталога загрузок!", "red"))
				input(self.NAME + "Удалите папку downloads и нажмите энтер...")
		# ===================
		os.chdir("..")  # возвращение в рабочую директорию
		os.rmdir("downloads")  # удаление папки, куда скачивались архивы
		# ===================
		return proxy_list


class Main_parser(Parsing):
	"""docstring for Main"""
	
	def __init__(self, *args, **kwargs):
		super().__init__()
		
	def main_main(self):
		return Parsing.parsing(self)



if __name__ == '__main__':
	starting = Main_parser()
	a = starting.main_main()
