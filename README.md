# rpi_remote_mqtt

sudo pacman -S python-paho-mqtt
mosquitto_sub -h HOST -p PORT -u USER -P PASS -v -t "#"
mosquitto_pub -h HOST -p PORT -u USER -P PASS -t 'device_outdoor/input/light' -m '0'

sudo pacman -S python-periphery
sudo pacman -S bindW

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
sudo gpasswd -a alarm wheel

/etc/udev/rules.d/alarm-gpio.rules
SUBSYSTEM=="gpio", ACTION=="add", PROGRAM="/bin/sh -c 'chgrp -R gpio /dev/gpiochip* && chmod -R g+rw /dev/gpiochip*'"

/etc/udev/rules.d/alarm-i2c.rules
SUBSYSTEM=="i2c-dev", ACTION=="add", PROGRAM="/bin/sh -c 'chgrp -R gpio /dev/i2c* && chmod -R g+rw /dev/i2c*'"

# connect to rpi using usb tethering
- `adb devices`
- `adb tcpip 5555`
- `adb connect IP`
- turn on usb tethering
- `adb shell`
- `ip -4 addr show rndis0`
- `for i in `seq 255`; do ping -c 1 192.168.135.$i | grep "time="; done`
for i in `seq 255`; do ping -c 1 `ip -4 addr show dev rndis0 | grep inet | tr -s " " | cut -d" " -f3 | head -n 1 | cut -d "." -f 1,2,3`.$i | grep "time="; done


/etc/systemd/system/getty@tty1.service.d/override.conf
[Service]
ExecStart=
ExecStart=-/usr/bin/agetty --autologin username --noclear %I $TERM

/etc/polkit-1/rules.d/50-org.freedesktop.NetworkManager.rules
polkit.addRule(function(action, subject) {
  if (action.id.indexOf("org.freedesktop.NetworkManager.") == 0 && subject.isInGroup("network")) {
    return polkit.Result.YES;
  }
});