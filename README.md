# rpi_remote_mqtt

sudo pacman -S python-paho-mqtt
mosquitto_sub -h HOST -p PORT -u USER -P PASS -v -t "#"
mosquitto_pub -h HOST -p PORT -u USER -P PASS -t 'device_outdoor/input/light' -m '0'
