echo 1500 > /proc/sys/vm/dirty_writeback_centisecs

echo 5 > /proc/sys/vm/laptop_mode


echo 10 > /sys/module/snd_ac97_codec/parameters/power_save 

echo min_power > /sys/class/scsi_host/host0/link_power_management_policy

amixer set Master mute nocap
amixer set Capture mute nocap

echo Y > /sys/module/snd_hda_intel/parameters/power_save_controller

