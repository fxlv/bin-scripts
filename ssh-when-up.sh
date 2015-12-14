#!/bin/bash
# 
# Initial BASH version of ssh-when-up
# Deprecated in favor of ssh-when-up.py
#

function usage {
    echo
    echo "Usage:"
    echo "$0 <hostname>"
    echo
    exit 0
}
if [ $# -ne 1 ]; then
    usage
fi

host=$1
retry_counter=0
max_sleep_time=60
start_time=$(date +%s)
last_print=$(date +%s)

function sleepy() {
        # sleep for 1 - 3 seconds
        sleep_time=$[( $RANDOM % 3 )]
            current_time=$(date +%s)
            down_time=$(($current_time - $start_time))
            time_since_last_print=$(($current_time - $last_print))
            if [ $time_since_last_print -lt 15 ]; then
                echo -n "."
            else
                echo
                echo "[ $date ] Host $host is down for $down_time seconds, sleeping."
                last_print=$current_time
            fi
            sleep $sleep_time
}

# first check if this is a hostname and if it is check if it can be resolved
if echo "$host" | grep -E "^[0-9\.]+$" > /dev/null; then
    echo "Connecting to IP address $host"
else
    if ! host "$host" > /dev/null; then
        echo "Failed to do hostname resolution for $host"
        exit 1
    fi
fi

while true; do
        if ssh -o ConnectTimeout=2 "$host" id 2>1 | grep -q "uid="; then
            current_time=$(date +%s)
            down_time=$(($current_time - $start_time))
            echo "Host is up after $down_time seconds"
            ssh "$host"
            exit $?
        else
            date=$(date)
            sleepy
            retry_counter=$(($retry_counter +1 ))
        fi
done

