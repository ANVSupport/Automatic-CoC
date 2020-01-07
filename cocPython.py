import checks as checks

# A Script that generates a report about the Info Needed for CoC
# Written By Gilad Ben-Nun
# All checking functions are in the check.py file


def main():
	specs = checks.hw_checks()
	print(specs)
	#checks.hw_checks()
	apps = ["git", "htop"]
	#check_installed_apps(apps)
if __name__ == '__main__':
	main()