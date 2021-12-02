# rpi_remote_mqtt

sudo pacman -S python-paho-mqtt
mosquitto_sub -h HOST -p PORT -u USER -P PASS -v -t "#"
mosquitto_pub -h HOST -p PORT -u USER -P PASS -t 'device_outdoor/input/light' -m '0'

sudo pacman -S python-periphery

https://ozzmaker.com/i2c/
sudo pacman -S i2c-tools
/etc/modules-load.d/raspberry_i2c.conf
i2c-dev
i2c-bcm2708

/boot/config.txt
dtparam=i2c_arm=on
dtparam=i2c1=on

groupadd gpio
usermod -a -G gpio alarm

/etc/udev/rules.d/10-alarm-gpio.rules
SUBSYSTEM=="gpio", ACTION=="add", PROGRAM="/bin/sh -c 'chgrp -R gpio /dev/gpiochip* && chmod -R g+rw /dev/gpiochip*'"

/etc/udev/rules.d/10-alarm-i2c.rules
SUBSYSTEM=="i2c-dev", ACTION=="add", PROGRAM="/bin/sh -c 'chgrp -R gpio /dev/i2c* && chmod -R g+rw /dev/i2c*'"