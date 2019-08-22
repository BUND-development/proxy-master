# -*- coding: utf-8 -*-

import os  # Работа с системой
def cls():
	'''Очистка консоли'''
	os.system('cls' if os.name=='nt' else 'clear')
# ============================================================
def coloring(string, color):
	'''Мой мини-модуль для раскрашивания текста'''
	if color == "red":
		string = "\x1b[31m" + string + "\x1b[0m"
	elif color == "green":
		string = "\x1b[32m" + string + "\x1b[0m"
	elif color == "yellow":
		string = "\x1b[33m" + string + "\x1b[0m"
	elif color == "blue":
		string = "\x1b[34m" + string + "\x1b[0m"
	else:
		pass
	return string
# ============================================================
try:
	# установка нужных библиотек
    os.system("pip install requests pysocks urllib3 bs4 colorama lxml" if os.name=="nt" else "pip3 install --user requests pysocks urllib3 bs4 colorama lxml")
except:
    pass
finally:
    cls()   # очистка командной строки
# ============================================================
try:
	import requests  # запросы по сети
	import bs4  # обработка html файлов
	import re  # регулярные исключения
	import zipfile  # работа с архивами
	import random  # случайные числа
	import sys  # работа с системой
	import colorama  # цветной текст
	colorama.init()  # инициация в консоли цветного текста
	import urllib3  # отключение предупреждений об незащищенном соединении
	from time import sleep  # режим ожидания
except:
	print(coloring("Ошибка импортирования модулей!", "red"))
	exit(1)
else:
	print(coloring("Модули ипортированы успешно!", "green"))
# ============================================================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # отключение уведомлений об незащищенности соединения


# ============================================================


class Data():
	'''Класс с настройками'''

	def __init__(self):
		self.FILENAME = "proxies-parsed.txt"  # файл импорта
		self.MAINURLS = (  # сайты, с которых парсится основная часть проксей путем регулярных исключений и архивов
			"http://www.proxyserverlist24.top/",
			"http://www.socks24.org",
			#"http://www.vipsocks24.net/",
			#"http://www.socksproxylist24.top/",
			#"http://www.sslproxies24.top/"
			)
		self.SOMELINKS = "something.txt" # файл, нужный для дебаггинга
		self.TIMEOUT = (30, 50)
		self.DOWNLOADTIMEOUT = 10
		#self.SLEEPTIME = random.randint(10, 30)  # приостановка программы перед следующим запросом



class Parsing(Data):
	''' Класс парсинга прокснй и архивов с проксями'''

	def __init__(self):
		super().__init__()
		self.download_files = []  # список имен zip файлов, которые были скачаны 
		self.proxies_list = []  # список проксей, спарсенных с самих сайтов
		self.debug_list = []  # список для дебаггинга, в релизных версиях не используется

# ============================================================
	# метод компоновки единого списка проксей из всех
	def getting_all(self):
		'''Пока не используется'''
		pass

# ============================================================
	# получение всех ссылок со страницы
	def get_links(self, url):
		results = requests.get(url, timeout=20, verify=False)  # поулчение страницы
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
		#links = list(links)
		return links  # возвращение списка

# ============================================================
	# анализирование найденных юрлов
	def analizing_urls(self, list_urls):
		for url_name in list_urls:  # проходимся по всем найденным ссылкам
			# ===================
			try:
				answer = requests.get(url_name, timeout=self.TIMEOUT, verify=False)  # получения страницы этой ссылки
			except:
				print(coloring("Не удалось получить страницу юрла.", "yellow"))
				continue
			else:
				print(coloring("Страница успешно скачана, проверяется наличие проксей...", ""))
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
						print(coloring("Обнаружена ссылка на скачивание> {0}".format(str(link)), ""))
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
									print(coloring("Обнаружена прямая ссылка на скачивание> {0}".format(str(download)), "green"))
									# ===================
									#file = requests.get(download, stream = True)  # скачивание архива
									#print(coloring(
										#"Приостановка программы для предотвращения блокировки на {0} секунд".format(str(self.SLEEPTIME)),
										#"green"
										#))
									#time.sleep(self.SLEEPTIME)
									print(coloring("Скачивание файла...", ""))
									#self.SLEEPTIME = random.randint(20, 30)
									try:
										file = requests.get(download, timeout=self.DOWNLOADTIMEOUT)
									except Exception as a:
										print(coloring("Ошибка загрузки файла!", "red"))
										raise a
									else:
										print(coloring("Файл успешно загружен в память, идет запись на диск...", ""))

									# ===================
									filename = os.getcwd() + "/downloads/" + str(random.randint(1, 1000)) + ".zip"  # загрузка архива в папку 
									# ===================
									with open(filename, mode="wb") as zipfile:  # запись архива в файл
										zipfile.write(file.content)  # запись zip файла
										#print(coloring("Файл сохранен успешно!", "green"))
										#self.download_files.append(filename)  # запись в список загруженных файлов
										# ===================
										print(
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
				print(
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
				self.proxies_list.extend(proxies_find)  # добавление списка проксей к уже имеющимся прокси
			else:
				print(coloring("Не найдено проксей на скачанной странице.", "yellow"))
		# ==============================================
		print(
			coloring(
				"Всего напарсено с сайтов {0} проксей, ".format(len(self.proxies_list)),
				""
				),
			end=""
			)
		# ===================
		self.proxies_list = set(self.proxies_list)  # опять очистка от дублей
		print(
			coloring(
				"из них {0} уникальные.".format(len(self.proxies_list)),
				"green"
				)
			)
		# ===================
		return self.proxies_list  # возвращаем список проксей

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
			list_p.extend(Parsing.get_links(self, url))  # получение ссылок
		# ===================
		proxies.extend(Parsing.analizing_urls(self, list_p))  # получение списка проксей
		# ===================
		proxies.extend(Parsing.open_archives(self))  # добавление архивов проксями к результату
		# ===================
		print(
			coloring(
				"Итоговое количество проксей {0}, ".format(len(proxies)),
				""
				),
			end=""
			)
		proxies = set(proxies)
		print(
			coloring(
				"из которых {0} уникальные.".format(len(proxies)),
				"green"
				)
			)
		return proxies
		#with open(self.FILENAME, mode="w", encoding="UTF-8") as file:
			#for i in proxies:
				#file.write(i + "\n")

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
					# ===================
					for i2 in os.listdir():  
						try:
							if '.txt' in i2:
								with open(i2, mode="r", encoding="utf-8") as txtfile:  # открытие Txt файла с проксями
									read = txtfile.read()  # прочтение содержимого файла
									read = read.split('\n')  # разделение содержимого по новой строке
									# ===================
									try:
										read.remove("")  # удаление строки с пустым символом если есть
									except:
										pass
									# ===================
									proxy_list.extend(read)  # добавление к уже имеющимся
									# ===================
									os.remove(i2)  # удаление txt
									os.remove(i)  # удаление архива
							else:
								continue
						except:
							print(
								coloring(
									"Не удалось обработать файл {0}, но распаковка прошла успешно.".format(i2),
									"yellow"
									)
								)
							continue
						# ===================
						else:
							print(
								coloring(
									"Удалось успешно прочесть .txt файл! \n Получено {0} проксей.".format(len(proxy_list)),
									"green"
									)
								)
							# ===================
							for i in os.listdir():
								if ".zip" in i:
									continue
								else:
									try:
										os.remove(i)
									except:
										print(coloring("Ошибка очистки каталога загрузок!", "red"))
										input("Удалите все не .zip файлы и нажмите энтер...")
				# ===================
				except:
					print(
						coloring(
							"Не удалось распаковать загруженный архив: {0}".format(i),
							"red"
							)
						)
					badtryes += 1
					for i in os.listdir():
						if ".zip" in i:
							continue
						else:
							try:
								os.remove(i)
							except:
								print(coloring("Ошибка очистки каталога загрузок downloads!", "red"))
								input("Удалите все не .zip файлы и нажмите энтер...")
				# ===================
		# ===================
		print(
			coloring(
				"Удалось успешно распаковать скачанные архивы! \n Получено {0} проксей, из них ".format(len(proxy_list)),
				""
				),
			end=""
			)
		# ===================
		proxy_list = set(proxy_list)  # очистка от дублей
		# ===================
		print(
			coloring(
				"{0} уникальные.".format(len(proxy_list)),
				"green"
				)
			)
		print(badtryes * 
			coloring(
				"Не удалось распаковать или обработать {0} архивов.".format(str(badtryes)),
				"red"
				),
			end= bool(badtryes) * "\n"
			)
		# ===================
		for i in os.listdir():
			try:
				os.remove(i)
			except:
				print(coloring("Ошибка очистки каталога загрузок!", "red"))
				input("Удалите папку downloads и нажмите энтер...")
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
