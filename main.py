import checks as checks
import json
# A Script that generates a report about the Info Needed for CoC
# Written By Gilad Ben-Nun
# All checking functions are in the check.py file


def main():
	Report = {}
	apps = ["git", "htop", "figlet"]
	license_details = checks.license_check()
	if license_details is None:
		license_details = "Error fetching license data.. is BT isntalled?"


	Report["Hardware Details"] = checks.hw_checks()
	Report["Installed Apps"] = checks.check_installed_apps(apps)
	Report["License"] = license_details
	Report["Yaml Edits"] = checks.file_modifications_checks()
	Report["Fstab Entry"] = checks.storage_mount_checks()

	formatted_Report = json.dumps(Report, indent=3)
	print(formatted_Report)


if __name__ == '__main__':
	main()