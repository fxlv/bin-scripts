#!/bin/bash
#xrandr --output HDMI2 --mode 1920x1200 --rate 60
if xrandr |grep "HDMI2 connected"
then
    xrandr --output HDMI2 --auto --primary
#xrandr --output VGA1 --auto --primary
    sleep 1
    xrandr --output LVDS1 --off
    notify-send 'Ext monitor connected' 'External monitor connected and resolution is adjusted.'
else
    echo "HDMI2 not connected"
fi
