#!/bin/bash
#xrandr --output HDMI2 --mode 1920x1200 --rate 60
xrandr --output HDMI2 --off
xrandr --output HDMI1 --off
xrandr --output VGA1 --off
sleep 1
xrandr --output LVDS1 --mode 1366x768 --primary
echo "Will now turn of all the other screens"
notify-send 'Ext monitor connected' 'External monitor connected and resolution is adjusted.'
