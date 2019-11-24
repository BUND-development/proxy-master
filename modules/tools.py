# -*- coding: utf-8 -*-

from modules import logwrite
from asyncio import iscoroutine

def errorsCap(func):
	if iscoroutine(func):
		async def wrapper(*args, **kwargs):
			try:
				result = func(*args, **kwargs)
			except Exception as e:
				logwrite.log(e, func.__doc__)
			else:
				return result
	else:
		def wrapper(*args, **kwargs):
			try:
				result = func(*args, **kwargs)
			except Exception as e:
				logwrite.log(e, func.__doc__)
			else:
				return result
	return wrapper

def loopResponse(response, name):
	for i in response:
		if i != None:
			logwrite.log(i, name)

@errorsCap
def testFunc_(value):
	'''
	Func for test error
	'''
	if value == 1:
		raise Exception("Test")
	else:
		return value*2


if __name__ == '__main__':
	testFunc(1)
