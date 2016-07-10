#!/bin/bash
if [ -z $1 ]; then
    echo "Please provide ILO hostname/IP as the first argument"
    exit 1
fi
ssh -o "PreferredAuthentications password" -oKexAlgorithms=diffie-hellman-group1-sha1   Administrator@${1}
