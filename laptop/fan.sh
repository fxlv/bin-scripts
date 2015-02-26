#!/bin/bash
function status {
    echo "--------------------------------"
    grep -E -e 'status:|speed:|level:' /proc/acpi/ibm/fan
    echo "--------------------------------"
    echo "Temperature:"
    echo "--------------------------------"
    sensors| grep -E -e 'C' 
    }
if [ -z $1 ]; then
    status
else
    echo "Setting fan speed to $1"
    sudo sh -c "echo level $1 > /proc/acpi/ibm/fan "
    status
fi

# echo level 0 > /proc/acpi/ibm/fan (fan off)
# echo level 2 > /proc/acpi/ibm/fan (low speed)
# echo level 4 > /proc/acpi/ibm/fan (medium speed)
# echo level 7 > /proc/acpi/ibm/fan (maximum speed)
# echo level auto > /proc/acpi/ibm/fan (automatic - default)
# echo level disengaged > /proc/acpi/ibm/fan (disengaged)
