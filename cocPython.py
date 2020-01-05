import os
import subprocess
import shutil
import logging

# A Script that generates a report about the Info Needed for CoC
# Written By Gilad Ben-Nun
def hw_checks():
	cpu_model = None
	ram_capacity = None
	hard_drives = None
	gpu_model = None
	# CPU Block
	cpu_p1 = subprocess.Popen(["cat", "/proc/cpuinfo"], stdout=subprocess.PIPE) 							# pipe into cpu_p2 stdin
	cpu_p2 = subprocess.Popen(["grep", "-m1", "model name"], stdin=cpu_p1.stdout, stdout=subprocess.PIPE) 	# find cpu name
	cpu_p1.stdout.close() 																					# close pipe if error
	cpu_model = str(cpu_p2.communicate()[0]).split(":")[1] 													#execute command

	# GPU Block
	try:
		gpu_model = subprocess.Popen(["nvidia-smi", "--list-gpus"])
		gpu_model = str(gpu_model.communicate()[0])
	except:
		try:
			gpu_model_p1 = subprocess.Popen(["lspci"], stdout=subprocess.PIPE)
			gpu_model_p2 = subprocess.Popen(["grep", "-i", "vga"], stdin=gpu_model_p1.stdout, stdout=subprocess.PIPE)
			gpu_model_p1.stdout.close()
			gpu_model = str(gpu_model_p2.communicate()[0])
			gpu_model = gpu_model.replace("\n","").replace(" ", "")
		except:
			gpu_model = "Failed to Fetch GPU Info"
			# TODO Logging, no driver installed
	# RAM Block
	try:
		ram_capacity_p1 = subprocess.Popen(["cat", "/proc/meminfo"], stdout=subprocess.PIPE)
		ram_capacity_p2 = subprocess.Popen(["grep", "-i", "memtotal"], stdin=ram_capacity_p1.stdout, stdout=subprocess.PIPE)
		ram_capacity_p1.stdout.close()
		ram_capacity = int(str(ram_capacity_p2.communicate()[0]).split()[1])
		ram_capacity = ram_capacity/1024
	except:
		ram_capacity = "Failed to Fetch RAM capacity"

	# HDD Block
	try:
		hdd_p1 = subprocess.Popen(["lsblk", "-io", "SIZE,KNAME,TYPE"], stdout=subprocess.PIPE)
		hdd_p2 = subprocess.Popen(["grep", "-i", "disk"], stdin=hdd_p1.stdout, stdout=subprocess.PIPE)
		#hdd_p3 = subprocess.Popen(["sort", "-nr"], stdin=hdd_p2.stdout, stdout=subprocess.PIPE)
		hdd_p1.stdout.close()
		hard_drives = str(hdd_p2.communicate()[0])
		hard_drives = hard_drives.replace("\n","").replace(" ", "")
	except:
		print("Couldn't Fetch HDD Info")
		# TODO Logging

	return cpu_model, ram_capacity, hard_drives, gpu_model
	#print(cpu_model)
	#print(ram_capacity)
	#print(hard_drives)
	#print(gpu_model)



def check_installed_apps(app_list):
	installed_apps=[]
	not_installed_apps=[]
	did_any_app_fail = False
	for app in app_list:
		is_installed = shutil.which(app)
		if is_installed is not None:
			installed_apps.append(app)
		else:
			not_installed_apps.append(app)
	for index, missing_app in enumerate(not_installed_apps):
		try:
			installation = subprocess.run(["sudo", "apt-get", "install", "-yqq", missing_app])
			if installation.returncode is 0:
				installed_apps.append(missing_app)
				not_installed_apps[index] = None
			else:
				print("error installing %s, please install manually", app)
		except:
				# TODO Log failure
				# TODO orginize tryblock vs if else
				print("couldn't install")


	for app in not_installed_apps:
		if app is not None:
			did_any_app_fail = True
		else:
			print("yikes")

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
	specs = hw_checks()
	print(specs)
	hw_checks()
	apps = ["git", "htop"]
	#check_installed_apps(apps)

if __name__ == '__main__':
	main()