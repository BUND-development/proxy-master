import os

def cls():
	'''Очистка консоли'''
	os.system('cls' if os.name=='nt' else 'clear')

try:
	os.system("pip install requests pysocks urllib3 bs4 colorama lxml pygeoip backoff termcolor" if os.name=="nt" else "pip3 install --user requests pysocks urllib3 bs4 colorama lxml pygeoip backoff termcolor")
except:
	pass
finally:
	cls()

if __name__ == '__main__':
	pass