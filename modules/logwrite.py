# -*- coding: utf-8 -*-



def log(error, module, **kwargs):
	with open("BUGREPORT", mode="a", encoding="UTF-8") as file:
		params ="\n"
		try:
			st = open("settings.ini", encoding="UTF-8")
			settings = st.read()
		except:
			settings = "ERROR .ini"
		else:
			st.close()
		for key in kwargs:
			params = params + "\n" + str(key) + ":" + str(kwargs[key])
		text_log = "\n============\nmodule: {0}\nerror:{1}\n--another params--{2}\n settings: {3}\n============\n".format(module, error, params, settings)
		file.write(text_log)


if __name__ == '__main__':
	pass