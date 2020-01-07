import os
import subprocess
import shutil
import logging
from decimal import Decimal
import re
import json

def file_modifications_checks():
	""" 
	Sets File Paths
	Needs to become more generic, right now only for Safeguard (1.20.0)

	"""
	hostname = subprocess.check_output("hostname").decode("utf-8").replace("\n","")
	logname = subprocess.check_output("logname").decode("utf-8").replace("\n","")


	docker_compose_yaml  = "/home/%s/docker-compose/1.20.0/docker-compose.yml" % logname
	profile_file = "/home/%s/.profile" % logname
	broadcaster_file = "/home/%s/docker-compose/1.20.0/env/broadcaster.env" % logname
	"""
	Sets Terms to search in those files

	"""
	nginx_hostname = "nginx-%s.tls.ai" % hostname
	api_hostname = "api-%s.tls.ai" % hostname
	moxa_mount_path = "/home/user/moxa-config:/home/user/moxa-config"	
	broadcaster_searching_lines = ["BCAST_MODBUS_IS_ENABLED=true", 
	"BCAST_MODBUS_CMD_PATH=/home/user/moxa-config/moxa_e1214.sh", 
	"BCAST_MODBUS_CAMERA_LIST_PATH=/home/user/moxa-config/cameraList.json"]

	with open(docker_compose_yaml, 'r') as stream:
		content = stream.read()
		nginx_count = content.count(nginx_hostname)
		api_count = content.count(api_hostname)
		moxa_mount_count = content.count(moxa_mount_path)

	with open(profile_file, 'r') as stream:
		content = stream.read()
		xhost_count = content.find("xhost +")
		if xhost_count is -1:
			xhost_count = "Not found"

	with open(broadcaster_file, 'r') as stream:
		content = stream.read()
		are_broadcaster_lines_correct = True
		for line in broadcaster_searching_lines:
			if content.find(line) is -1:
				are_broadcaster_lines_correct = False

	yaml_json = {}
	yaml_json["hostname"] = hostname
	yaml_json[nginx_hostname] = nginx_count
	yaml_json[api_hostname] = api_count
	yaml_json[moxa_mount_path] = moxa_mount_count
	yaml_json["xhost + inside .profile"] = xhost_count
	yaml_json["Are Broadcaster edits present"] = are_broadcaster_lines_correct
	return yaml_json



def storage_mount_checks():
	fstab_file = "/etc/fstab"
	entire_line = "No Matching Entry Found"
	with open(fstab_file, 'r') as stream:
		content = stream.read()
		for line in content.split("\n"):
			if "storage" in line:
				entire_line = line.strip()
	fstab_json = {}
	fstab_json["/etc/fstab entry"] = entire_line
	return fstab_json





def hw_checks():

	cpu_model = None
	ram_capacity = None
	hard_drives = None
	gpu_model = None

	# CPU Block
	cpu_p1 = subprocess.Popen(["cat", "/proc/cpuinfo"], stdout=subprocess.PIPE) 							# pipe into cpu_p2 stdin
	cpu_p2 = subprocess.Popen(["grep", "-m1", "model name"], stdin=cpu_p1.stdout, stdout=subprocess.PIPE) 	# find cpu name
	cpu_p1.stdout.close() 																					# close pipe if error
	cpu_model = clean_string(str(cpu_p2.communicate()[0]).split(":")[1])							     	#execute command

	# GPU Block
	try:
		gpu_model = subprocess.Popen(["nvidia-smi", "--list-gpus"], stdout=subprocess.DEVNULL)
		gpu_model = str(gpu_model.communicate()[0])
	except:
		try:
			gpu_model_p1 = subprocess.Popen(["lspci"], stdout=subprocess.PIPE)
			gpu_model_p2 = subprocess.Popen(["grep", "-i", "vga"], stdin=gpu_model_p1.stdout, stdout=subprocess.PIPE)
			gpu_model_p1.stdout.close()
			gpu_model = gpu_model_p2.communicate()[0]
		except:
			gpu_model = "Failed to Fetch GPU Info"
			# TODO Logging, no driver installed
	gpu_model = clean_string(gpu_model)


	# RAM Block
	try:
		ram_capacity_p1 = subprocess.Popen(["cat", "/proc/meminfo"], stdout=subprocess.PIPE)
		ram_capacity_p2 = subprocess.Popen(["grep", "-i", "memtotal"], stdin=ram_capacity_p1.stdout, stdout=subprocess.PIPE)
		ram_capacity_p1.stdout.close()
		ram_capacity_KB = Decimal(str(ram_capacity_p2.communicate()[0]).split()[1])
		ram_capacity_GB = Decimal(ram_capacity_KB/1024)
		ram_capacity_GB = round(ram_capacity_GB,2)
		ram_capacity_GB = clean_string(ram_capacity_GB)
	except:
		ram_capacity = "Failed to Fetch RAM capacity"

	# HDD Block
	try:
		hdd_p1 = subprocess.Popen(["lsblk", "-io", "SIZE,TYPE,KNAME"], stdout=subprocess.PIPE)
		hdd_p2 = subprocess.Popen(["grep", "-i", "disk"], stdin=hdd_p1.stdout, stdout=subprocess.PIPE)
		hdd_p1.stdout.close()
		hard_drives = str(hdd_p2.communicate()[0])
		hard_drives = clean_string(hard_drives)
	except:
		print("Couldn't Fetch HDD Info")
		# TODO Logging
	#Builds JSON to return to main

	specs_json = {}
	specs_json["CPU Model"] = cpu_model
	specs_json["RAM capacity"] = ram_capacity_GB
	specs_json["hard_drives"] = hard_drives
	specs_json["GPU Model"] = gpu_model

	return specs_json





def check_installed_apps(app_list):
	installed_apps=[]
	not_installed_apps=[]
	for app in app_list:
		is_installed = shutil.which(app)
		if is_installed is not None:
			installed_apps.append(app)
		else:
			not_installed_apps.append(app)
	for index, missing_app in enumerate(not_installed_apps):
		try:
			print("Installing %s... Please Wait" % (missing_app,))
			installation = subprocess.run(["sudo", "apt-get", "install", "-yqq", missing_app])
			if installation.returncode is 0:
				installed_apps.append(missing_app)
				print("%s installed" % (missing_app,))
				not_installed_apps[index] = None
			else:
				print("error installing %s, please install manually" % (app,))
		except Exception as err:
				# TODO Log failure
				# TODO orginize tryblock vs if else
				print("couldn't install")
				print(err)


	installed_apps_json = {}
	for installed_app in installed_apps:
		installed_apps_json[installed_app] = " .....Installed    V"

	for not_installed_app in not_installed_apps:
		installed_apps_json[not_installed_app] = ".....Not Installed    X"
		

	return installed_apps_json




def license_check():
	# Needs testing on Various BT machines...
	footprint = None
	expiration = None
	try:
		backend_container = subprocess.run("docker ps", "grep backend_", "awk '{print $1}'") # If it's docker-compose, extracts backend container
	except:
		try:
			backend_pod = subprocess.run("kubectl get pod", "grep edge-0", "awk '{print $1}'") # If it's kubernetes, extract backend pod
		except:
			pass
			# TODO log failure
		else:
			footprint = str(subprocess.run("kubectl exec -it backend_pod -c edge -- bash -c '/usr/local/bin/license-ver -o' ").stdout)
			expiration = str(subprocess.run("kubectl exec -it backend_pod -c edge -- bash -c '/usr/local/bin/license-ver -b' ").stdout)
	else:	
		footprint = str(subprocess.run(["docker", "exec", "-it", backend_container, "license-ver", "-o"]))
		expiration = str(subprocess.run(["docker", "exec", "-it", backend_container, "license-ver", "-b"]))
	license_json = {}
	license_json["System Footprint"] = footprint
	license_json["License Expiration"] = parse_date(expiration)
	return license_json

def parse_date(messy_date):
	date_list = list(messy_date)
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



def clean_string(string):
	string =  str(string)
	string = ' '.join(string.split()) # Replaces multipile white spaces with one.
	string = string.replace("\\n", "")
	string = string.replace("\'","")
	string = string.replace("b","")
	return string

