





def log(error, module, **kwargs):
	with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
		params ="\n"
		for key in kwargs:
			params = params + "\n" + str(key) + ":" + str(kwargs[key])
		text_log = "\n============\nmodule: {0}\nerror:{1}\n--another params--{2}\n============\n".format(module, error, params)
		file.write(text_log)

if __name__ == '__main__':
	pass