#!/bin/bash

function ison(){
	if grep status /proc/acpi/ibm/light |grep -q on
	then
		return 0
	else
		return 1
	fi
}

function switchon(){
	echo "on" > /proc/acpi/ibm/light
}
function switchoff(){
	echo "off" > /proc/acpi/ibm/light
}

if ! ison 
then
	switchon	
	sleep 1
	switchoff	
	sleep 1
	switchon
	sleep 1
	switchoff
else
    sudo /home/fx/bin/beep.sh
fi
