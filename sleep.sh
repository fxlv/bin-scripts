#!/bin/bash
echo "Going to sleep..."
sudo sh -c "echo -n mem > /sys/power/state"
