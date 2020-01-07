import checks as checks
import json
# A Script that generates a report about the Info Needed for CoC
# Written By Gilad Ben-Nun
# All checking functions are in the check.py file


def main():
	Report = {}
	apps = ["git", "htop", "figlet"]
	license_details = checks.Check_License()
	if license_details is None:
		license_details = "Error fetching license data.. is BT isntalled?"


	Report["Hardware Details"] = checks.Get_Hardware_Specifications()
	Report["Installed Apps"] = checks.Check_Installed_Apps(apps)
	Report["License"] = license_details
	Report["Yaml Edits"] = checks.Check_Modified_Files()
	Report["Fstab Entry"] = checks.Check_Storage_Mount()

	formatted_Report = json.dumps(Report, indent=3)
	print(formatted_Report)


if __name__ == '__main__':
	main()