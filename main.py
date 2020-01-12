import Agents as agent
import organize as org
import json
from datetime import datetime
import sys


"""
 A Script that generates a report about the Info Needed for CoC
 Written By Gilad Ben-Nun
 All checking functions are in the Agents.py file
"""

def main():
	is_Safeguard = False
	for index, arg in enumerate(sys.argv):
		if "type" in arg:
			try:
				if "SG" in sys.argv[index+1]:
					is_Safeguard = True
					print("Type set as SG")
			except:
				print("Invalid Arguments") 
	Checker_name = input("Enter You name: ")
	Report = {}
	license_details = agent.Check_License()
	if license_details is None:
		license_details = "Error fetching license data.. is BT installed?"
	Report_Details = {}
	Report_Details["Created On"] = str(datetime.now().strftime("%b %d %Y %H:%M:%S"))
	Report_Details["Checked By"] = str(Checker_name)
	Report["Report Details"] = Report_Details
	Report["Hardware Details"] = agent.Get_Hardware_Specifications()
	Report["Installed Apps"] = agent.Check_Installed_Apps("/tmp/apps.json")
	Report["License"] = license_details
	Report["Fstab Entry"] = agent.Check_Storage_Mount()
	if is_Safeguard:
		print("entered SG")
		Report["Yaml Edits"] = agent.Check_Modified_Files()
	#print("Writing this to file:")
	#print(org.Prettify_json(json.dumps(Report, indent=3)))
	report_path = "coc_"+org.get_hostname()+".txt"
	with open(report_path, "w") as report_file:
		report_file.write(org.Prettify_json(json.dumps(Report, indent=3)))
	print("Report written to %s" % (report_path))
	API_Details = {}
	API_Details["Details for API Integration"] = ""
	API_Details[str(org.get_hostname())] = agent.Get_IP_Address()
	print(org.Prettify_json(json.dumps(API_Details, indent=3)))




if __name__ == '__main__':
	main()