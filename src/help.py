#!/usr/bin/env python

import credentials

print("mosquitto_sub -h %s -p %s -u %s -P %s -v -t '#'" % (credentials.host, credentials.port, credentials.user, credentials.password))
print("mosquitto_pub -h %s -p %s -u %s -P %s -t 'device_outdoor/input/light' -m '0'" % (credentials.host, credentials.port, credentials.user, credentials.password))
