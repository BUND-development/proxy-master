import os

def cls():
	'''Очистка консоли'''
	os.system('cls' if os.name=='nt' else 'clear')

try:
	if os.name=="nt":
		os.system("pip install requests pysocks urllib3 bs4 colorama lxml pygeoip backoff termcolor configparser")
	else:
		os.system("pip3 install --user requests pysocks urllib3 bs4 colorama lxml pygeoip backoff termcolor configparser")
except:
	pass
finally:
	cls()

if __name__ == '__main__':
	pass