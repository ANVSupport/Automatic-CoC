import os
from subprocess import run
import shutil

# A Script that generates a report about the Info Needed for CoC
# Written By Gilad Ben-Nun
def hw_checks():
	cpu_model = str(run("cat /proc/cpuinfo", "grep -m1 \"model name\"", "awk -F: '{print $2}'").stdout)
	cpu_model = cpu_model.replace("\n", "")
	# Can't be tested on this dev pc, it has no nvidia gpu, uncomment in final
	# gpu_model = str(run("nvidia-smi --list-gpus").stdout)
	ram_capacity = str(run("cat /proc/meminfo", "grep -i MemTotal" , "awk -F: '{print $2}'").stdout)
	ram_capacity = ram_capacity.replace("\n", "").replace(" ", "")
	hard_drives = str(run("lsblk -io SIZE,KNAME,TYPE" , "grep disk" , "sort -nr").stdout)
	hard_drives = hard_drives.replace("\n", "").split(" ")
	return cpu_model, ram_capacity, hard_drives[0] #, gpu_model
def check_installed_apps(app_list):
	for app in app_list:
		is_installed = shutil.which(app)
		print(is_installed)
def main():
	# specs = hw_checks()
	# print(specs)
	apps = ["git", "htop"]
	check_installed_apps(apps)

if __name__ == '__main__':
	main()