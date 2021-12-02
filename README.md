# rpi_remote_mqtt

sudo pacman -S python-paho-mqtt
mosquitto_sub -h HOST -p PORT -u USER -P PASS -v -t "#"
mosquitto_pub -h HOST -p PORT -u USER -P PASS -t 'device_outdoor/input/light' -m '0'

groupadd gpio
usermod -a -G gpio alarm

/etc/udev/rules.d/10-alarm-gpio.rules
SUBSYSTEM=="gpio", ACTION=="add", PROGRAM="/bin/sh -c 'chgrp -R gpio /dev/gpiochip* && chmod -R g+rw /dev/gpiochip*'"