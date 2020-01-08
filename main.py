import Agents as agent
import organize as org
import json
"""
 A Script that generates a report about the Info Needed for CoC
 Written By Gilad Ben-Nun
 All checking functions are in the Agents.py file
"""

def main():
	Report = {}
	license_details = agent.Check_License()
	if license_details is None:
		license_details = "Error fetching license data.. is BT isntalled?"


	Report["Hardware Details"] = agent.Get_Hardware_Specifications()
	Report["Installed Apps"] = agent.Check_Installed_Apps("apps.json")
	Report["License"] = license_details
	Report["Yaml Edits"] = agent.Check_Modified_Files()
	Report["Fstab Entry"] = agent.Check_Storage_Mount()

	print(org.Prettify_json(json.dumps(Report, indent=3)))




if __name__ == '__main__':
	main()