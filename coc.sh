#! /bin/bash

# This preforms as many CoC checks as possible automatically..
# Some checks require GUI use and so need to be done manually..

HW_specs(){
	local CPU_Model
	local GPU_Model
	local RAM_Amount
	local HDD_Details
	CPU_Model=$(< /proc/cpuinfo grep -m1 "model name" | awk -F: '{print $2}')
	GPU_Model=$(nvidia-smi --list-gpus) # to be tested how it needs to be formatted..
	RAM_Amount=$(< /proc/meminfo grep -i "MemTotal" | awk -F: '{print $2}') # Need to convert to GB from Kb
	HDD_Details=$(lsblk -io SIZE,KNAME,TYPE | grep disk | sort -nr | awk -F" " '{print $1}') # test output to see if it works for more than 1 drive
	echo "CPU Model: " "$CPU_Model"
	echo "GPU Model: " "$GPU_Model"
	echo "RAM: " "$RAM_Amount"
	echo "HDD: " "$HDD_Details"
}
Installed_Apps(){
	appList=(teamviewer htop curl vim net-tools openssh-server)
	for app in "${appList[@]}"; do

		if ! [ -x "$(command -v "$app")" ]; then
		  echo "Error, $app not installed, would you like to install? [y/n]" >&2
		  local yn1
		  read -r "$yn1"
		  case "$yn1" in
		  	y|Y) apt install -qqy "$app";;
			n|N) echo "skipping...";;
			*)echo "Invalid choice... exiting";exit 1;;
		 esac
		else
			echo "$app is Installed"

		fi
	done
}