import subprocess

def Parse_Date(messy_date):
	try:
		date_list = list(messy_date)
	except TypeError as err:
		return "No Date"
	Year = None
	Months = None
	Days = None
	Date = None
	try:
		Year = "".join(date_list[0:4])
		Months = "".join(date_list[4:6])
		Days = "".join(date_list[6:8])
		Date = "%s - %s - %s" % (Days, Months, Year)
	except Exception as err:
		print(err)
	return Date

def Clean(string):
	string =  str(string)
	string = ' '.join(string.split()) # Replaces multipile white spaces with one.
	string = string.replace("\\n", "")
	string = string.replace("\'","")
	string = string.replace("b","")
	return string

def get_logname():
	return subprocess.check_output("logname").decode("utf-8").replace("\n","")
def get_hostname():
	return subprocess.check_output("hostname").decode("utf-8").replace("\n","")

def Prettify_json(formatted_json):
    return str(formatted_json).replace("{","").replace("}","").replace(",","").replace('\"',""  )
def Prettify_list(lst):
	final_string = ""
	for item in lst:
		final_string = final_string+item+"\n"
	return final_string