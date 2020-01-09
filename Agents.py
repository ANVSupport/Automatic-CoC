import os
import subprocess
import shutil
import logging
from decimal import Decimal
import re
import json
import organize as org
from datetime import datetime

""" 			Logger Block, sets up general Logging.			"""
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s")
file_handler = logging.FileHandler('coc.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info("Report Started On %s" % (str(datetime.now().strftime("%b %d %Y %H:%M:%S"))))


def Test_Moxa_Permissions():
	logname = subprocess.check_output("logname").decode("utf-8").replace("\n","")
	cameraListjson = "/home/%s/moxa-config/cameraList.json" % (logname)
	moxascript = "/home/%s/moxa-config/moxa_e1214.sh" % (logname)
	json_Permissions = subprocess.check_output(["bash", "PermissionTester.sh", cameraListjson]).decode("utf-8").strip()
	moxa_Permissions = subprocess.check_output(["bash", "PermissionTester.sh", moxascript]).decode("utf-8").strip()
	permissions = {}
	permissions[cameraListjson] = json_Permissions
	permissions[moxascript] = moxa_Permissions
	return permissions



def Check_Modified_Files():
	""" 
	Sets File Paths
	Needs to become more generic, right now only for Safeguard (1.20.0)

	"""
	yaml_json = {}
	hostname = subprocess.check_output("hostname").decode("utf-8").replace("\n","")
	logname = subprocess.check_output("logname").decode("utf-8").replace("\n","")
	docker_compose_path = "/home/"+logname+"/docker-compose/"
	docker_version = subprocess.check_output(["ls", docker_compose_path]).decode("utf-8").strip()
	docker_compose_path = str(docker_compose_path)+str(docker_version)+"/"
	dockerfile = subprocess.run(["find", docker_compose_path, "-regextype", "posix-extended", "-regex", 
		".*docker\\-compose\\-(local\\-)?gpu\\.yml"],
		 stdout=subprocess.PIPE)
	docker_compose_yaml = dockerfile.stdout.decode("utf-8").strip()
	profile_file = "/home/%s/.profile" % logname
	broadcaster_file = docker_compose_path+"/env/broadcaster.env"
	"""
	Sets Terms to search in those files

	"""
	nginx_hostname = "nginx-%s.tls.ai" % hostname
	api_hostname = "api-%s.tls.ai" % hostname
	moxa_mount_path = "/home/user/moxa-config:/home/user/moxa-config"	
	broadcaster_searching_lines = ["BCAST_MODBUS_IS_ENABLED=true", 
	"BCAST_MODBUS_CMD_PATH=/home/user/moxa-config/moxa_e1214.sh", 
	"BCAST_MODBUS_CAMERA_LIST_PATH=/home/user/moxa-config/cameraList.json"]
	try:
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
			else:
				xhost_count = "Found"

		with open(broadcaster_file, 'r') as stream:
			content = stream.read()
			are_broadcaster_lines_correct = True
			for line in broadcaster_searching_lines:
				if content.find(line) is -1:
					are_broadcaster_lines_correct = False
	except FileNotFoundError as err:
		logger.error("Error While Openig YAML and profile files: \n \t\t %s" % (err))
		return yaml_json
	yaml_json["Hostname"] = hostname
	yaml_json[nginx_hostname] = str(nginx_count)+"/3"
	yaml_json[api_hostname] = str(api_count)+"/7"
	yaml_json[moxa_mount_path] = "    "+str(moxa_mount_count)+"/1"
	yaml_json["Moxa Permissions"] = Test_Moxa_Permissions()
	yaml_json["xhost + inside .profile"] = xhost_count
	yaml_json["Are Broadcaster edits present"] = are_broadcaster_lines_correct
	return yaml_json

def Check_Storage_Mount():
	fstab_file = "/etc/fstab"
	entire_line = None
	with open(fstab_file, 'r') as stream:
		content = stream.read()
		for line in content.split("\n"):
			if "storage" in line:
				entire_line = line.strip()
	fstab_json = {}
	if entire_line is None:
		logger.warning("No Matching Fstab Entry Found")
		entire_line  = "No Matching Entry Found"
	fstab_json["/etc/fstab entry"] = entire_line
	return fstab_json

def Get_Hardware_Specifications():

	cpu_model = None
	ram_capacity = None
	hard_drives = None
	gpu_model = None

	# CPU Block
	try:
		cpu_p1 = subprocess.Popen(["cat", "/proc/cpuinfo"], stdout=subprocess.PIPE) 							# pipe into cpu_p2 stdin
		cpu_p2 = subprocess.Popen(["grep", "-m1", "model name"], stdin=cpu_p1.stdout, stdout=subprocess.PIPE) 	# find cpu name
		cpu_p1.stdout.close() 																					# close pipe if error
		cpu_model = org.Clean(str(cpu_p2.communicate()[0]).split(":")[1])							     	#execute command
	except:
		logger.warning("Could not Get CPU Name")		
	# GPU Block
	try:
		gpu_model = subprocess.Popen(["nvidia-smi", "--list-gpus"], stdout=subprocess.PIPE)
		gpu_model = str(gpu_model.communicate()[0])
	except:
		logger.warning("Can't cummunicate with nvidia GPU")
		try:
			gpu_model_p1 = subprocess.Popen(["lspci"], stdout=subprocess.PIPE)
			gpu_model_p2 = subprocess.Popen(["grep", "-i", "vga"], stdin=gpu_model_p1.stdout, stdout=subprocess.PIPE)
			gpu_model_p1.stdout.close()
			gpu_model = gpu_model_p2.communicate()[0]
		except:
			logger.error("Could not Fetch GPU Info")
	gpu_model = org.Clean(gpu_model)


	# RAM Block
	try:
		ram_capacity_p1 = subprocess.Popen(["cat", "/proc/meminfo"], stdout=subprocess.PIPE)
		ram_capacity_p2 = subprocess.Popen(["grep", "-i", "memtotal"], stdin=ram_capacity_p1.stdout, stdout=subprocess.PIPE)
		ram_capacity_p1.stdout.close()
		ram_capacity_KB = Decimal(str(ram_capacity_p2.communicate()[0]).split()[1])
		ram_capacity_GB = Decimal(ram_capacity_KB/1024/1024)
		ram_capacity_GB = round(ram_capacity_GB,2)
		ram_capacity_GB = org.Clean(ram_capacity_GB)
	except:
		logger.error("Could Not Fetch RAM Capacity")

	# HDD Block
	try:
		hdd_p1 = subprocess.Popen(["lsblk", "-io", "SIZE,TYPE,KNAME"], stdout=subprocess.PIPE)
		hdd_p2 = subprocess.Popen(["grep", "-i", "disk"], stdin=hdd_p1.stdout, stdout=subprocess.PIPE)
		hdd_p1.stdout.close()
		hard_drives = str(hdd_p2.communicate()[0].decode("utf-8"))
		hard_drives = hard_drives.replace("disk ", "at /dev/")
		hard_drives = hard_drives.split(sep="\n")
		#hard_drives = org.Clean(hard_drives)
	except:
		logger.error("Could not Fetch HDD Info")

	specs_json = {}
	specs_json["CPU Model"] = cpu_model
	specs_json["RAM capacity"] = str(ram_capacity_GB)+" GB"
	specs_json["Hard Drives"] = hard_drives
	specs_json["GPU Model"] = gpu_model

	return specs_json

def Check_Installed_Apps(json_filename):
	installed_apps=[]
	not_installed_apps=[]
	with open(json_filename, "r") as stream:
		app_dict = json.load(stream)

	for app_name, apt_install_name in app_dict.items():
		is_installed = shutil.which(app_name)
		if is_installed is not None:
			installed_apps.append(app_name)
		else:
			not_installed_apps.append(apt_install_name)
	for index, missing_app in enumerate(not_installed_apps):
		try:
			print("Installing %s... Please Wait \n\n" % (missing_app,))
			installation = subprocess.run(["sudo", "apt-get", "install", "-yqq", missing_app])
			if installation.returncode is 0:
				installed_apps.append(missing_app)
				logger.info("Installed %s using apt-get" % (missing_app))
				not_installed_apps[index] = None
			else:
				logger.error("could not install %s, return code: %d" % (missing_app, installation.returncode))
		except Exception as err:
				logger.error("Could not Install %s, Exception: %s" % (missing_app, err))


	installed_apps_json = {}
	number_of_installed_apps = 0
	number_of_not_installed_apps = 0
	for installed_app in installed_apps:
		installed_apps_json[installed_app] = " .....  Installed    V"
		number_of_installed_apps = number_of_installed_apps+1

	for not_installed_app in not_installed_apps:
		if not_installed_apps is not None:
			installed_apps_json[not_installed_app] = ".....  Not Installed    X"
			number_of_not_installed_apps = number_of_not_installed_apps+1
	logger.info("Installed apps: %d" % (number_of_installed_apps))
	logger.info("Not Installed Apps: %d" % (number_of_not_installed_apps))
		

	return installed_apps_json

def Check_License():
	footprint = None
	expiration = None
	try:
		backend_p1 = subprocess.Popen(["docker", "ps"], stdout=subprocess.PIPE)
		backend_p2 = subprocess.Popen(["grep", "-i", "backend_"], stdin=backend_p1.stdout, stdout=subprocess.PIPE)
		backend_p1.stdout.close()
		backend_container = str(backend_p2.communicate()).replace("(b\'","")
		backend_container = backend_container.split()[0]
		if "backend" in backend_container:
			footprint = str(subprocess.check_output(["docker", "exec", "-it", backend_container, "license-ver", "-o"]).decode("utf-8").strip())
			expiration = str(subprocess.check_output(["docker", "exec", "-it", backend_container, "license-ver", "-b"]).decode("utf-8").strip())
		# backend_container = subprocess.run("docker ps", "grep backend_", "awk '{print $1}'") # If it's docker-compose, extracts backend container

	except:
		try:
			edge_p1 = subprocess.Popen(["kubectl", "get", "pod"], stdout=subprocess.PIPE)
			edge_p2= subprocess.Popen(["grep", "edge-0"], stdin=edge_p1.stdout, stdout=subprocess.PIPE)
			edge_p1.stdout.close()
			edge_pod = str(edge_p2.communicate()[0]).split()[0]
			if "edge" in edge_pod:
				footprint = str(subprocess.check_output(["kubectl", "exec", "-it", edge_pod, "-c", "edge", "--", "bash", "-c", "/usr/local/bin/license-ver", "-o"]).decode("utf-8").strip())
				expiration = str(subprocess.check_output(["kubectl", "exec", "-it", edge_pod, "-c", "edge", "--", "bash", "-c", "/usr/local/bin/license-ver", "-b"]).decode("utf-8").strip())
		except:
			logger.error("Error While Extracting Backend Container/pod")
	if footprint is not None and expiration is not None:
		license_json = {}
		license_json["System Footprint"] = footprint
		license_json["License Expiration"] = org.Parse_Date(expiration)
		return license_json
	else:
		return None

