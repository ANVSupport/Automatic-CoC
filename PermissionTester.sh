#! /bin/bash
# To be used as utility inside Agents.py of the Automatic COC script
# checks the input file has rwx permissions

if [[ ! -f "$1" ]]
then
	echo "File Not Found!"
	exit

fi
if [[ -x "$1" ]] && [[ -r "$1" ]] && [[ -w "$1" ]]
then
     echo "rwx Permissions"
else
     chmod 777 "$1"
     if [[ -x "$1" ]] && [[ -r "$1" ]] && [[ -w "$1" ]]
     then
     	echo "Permissions: rwx (777)"
     else
     	echo "Missing permissions, Could not fix"
     	exit
     fi
fi
