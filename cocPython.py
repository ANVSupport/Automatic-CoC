import os
import subprocess
import shutil
import logging

# A Script that generates a report about the Info Needed for CoC
# Written By Gilad Ben-Nun
def hw_checks():
	cpu_model = str(subprocess.run("cat /proc/cpuinfo", "grep -m1 \"model name\"", "awk -F: '{print $2}'").stdout)
	cpu_model = cpu_model.replace("\n", "")
	# Can't be tested on this dev pc, it has no nvidia gpu, uncomment in final
	# gpu_model = str(subprocess.run("nvidia-smi --list-gpus").stdout)
	ram_capacity = str(subprocess.run("cat /proc/meminfo", "grep -i MemTotal" , "awk -F: '{print $2}'").stdout)
	ram_capacity = ram_capacity.replace("\n", "").replace(" ", "")
	hard_drives = str(subprocess.run("lsblk -io SIZE,KNAME,TYPE" , "grep disk" , "sort -nr").stdout)
	hard_drives = hard_drives.replace("\n", "").split(" ")
	return cpu_model, ram_capacity, hard_drives[0] #, gpu_model


def check_installed_apps(app_list):
	installed_apps=[]
	not_installed_apps=[]
	for app in app_list:
		is_installed = shutil.which(app)
		if is_installed is not None:
			installed_apps.extend(app)
		else:
			not_installed_apps.extend(app)
	for index, missing_app in enumerate(not_installed_apps):
		try:
			installation = subprocess.run(["sudo", "apt-get", "install", "-yqq", missing_app])
			if installation.returncode is 0:
				installed_apps.extend(missing_app)
				not_installed_apps[index] = None
			else:
				print("error installing %s, please install manually", app)
		except:
				# TODO Log failure
				# TODO orginize tryblock vs if else

def license_check():
	didProcessFail = False
	try:
		backend_container = subprocess.run("docker ps", "grep backend_", "awk '{print $1}'")
	except:
		try:
			backend_pod = subprocess.run("kubectl get pod", "grep edge-0", "awk '{print $1}'")
		except:
			print("Error finding backend...")
			didProcessFail = True
			# TODO log failure
		else:
			footprint = str(subprocess.run("kubectl exec -it backend_pod -c edge -- bash -c '/usr/local/bin/license-ver -o' ").stdout)
			expiration = str(subprocess.run("kubectl exec -it backend_pod -c edge -- bash -c '/usr/local/bin/license-ver -b' ").stdout)
	else:	
		footprint = str(subprocess.run(["docker", "exec", "-it", backend_container, "license-ver", "-o"]))
		expiration = str(subprocess.run(["docker", "exec", "-it", backend_container, "license-ver", "-b"]))
if footprint and expiration is not None and didProcessFail is False:
	return footprint, expiration
else:
	return None


def main():
	logger = logging.getLogger("Log")
	specs = hw_checks()
	print(specs)
	apps = ["git", "htop", "nvidia-smi"]
	check_installed_apps(apps)

if __name__ == '__main__':
	main()