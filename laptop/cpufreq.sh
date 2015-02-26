#!/bin/bash
cpus=( cpu0 cpu1 cpu2 cpu3 )

function status {
    for cpu in ${cpus[*]}
    do
        echo -n "$cpu: "
        cat /sys/devices/system/cpu/$cpu/cpufreq/scaling_governor
    done
}

# $1 has to be the scaling mode
# for example:
# 'set_cpu conservative'
function set_cpu {
    for cpu in ${cpus[*]}
    do
        echo "Setting mode: $cpu -> $1"
        sudo sh -c "echo $1 > /sys/devices/system/cpu/$cpu/cpufreq/scaling_governor"
        #cat /sys/devices/system/cpu/$cpu/cpufreq/scaling_governor
    done
}

function usage {
    echo 
    echo Please provide a command
    echo Available commands are:
    echo    status
    echo    conservative
    echo    ondemand
    echo    powersave
    echo
    echo
    exit 0

}

if [ $# -eq 0 ]; then
    status
    exit
else
    arg=$1
fi

if [ $arg == "status" ]; then
    status
elif [ $arg == "ondemand" ]; then
    set_cpu ondemand
elif [ $arg == "powersave" ]; then
    set_cpu powersave
else
    usage
fi
