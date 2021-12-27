#!/usr/bin/env python

import re
from glob import glob
import time
import os, sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common import log

logger = log.get()

w1DeviceFolder = '/sys/bus/w1/devices'


def get_thermometers():
    w1Devices = glob(w1DeviceFolder + '/*/')
    w1ThermometerCode = re.compile(r'28-\d+')
    thermometers = []
    for device in w1Devices:
        deviceCode = device[len(w1DeviceFolder) + 1:-1]
        if w1ThermometerCode.match(deviceCode):
            thermometers.append(deviceCode)
    return thermometers


def read_temp_raw(deviceCode):
    f = open(w1DeviceFolder + '/' + deviceCode + '/w1_slave', 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(deviceCode):
    lines = read_temp_raw(deviceCode)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(deviceCode)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    return None


def print_temperature(thermometer, data):
    logger.info("[DS18b20]: %s => %s" % (thermometer, data))


def test():
    thermometers = get_thermometers()
    for thermometer in thermometers:
        print_temperature(thermometer, read_temp(thermometer))


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
