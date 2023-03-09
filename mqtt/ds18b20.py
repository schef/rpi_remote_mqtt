#!/usr/bin/env python
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import re
from glob import glob
import time


class Ds18b20:
    def __init__(self, address):
        self.address = address
        self.w1DeviceFolder = '/sys/bus/w1/devices'

    def get_thermometers(self):
        w1Devices = glob(self.w1DeviceFolder + '/*/')
        w1ThermometerCode = re.compile(r'28-\d+')
        thermometers = []
        for device in w1Devices:
            deviceCode = device[len(self.w1DeviceFolder) + 1:-1]
            if w1ThermometerCode.match(deviceCode):
                thermometers.append(deviceCode)
        return thermometers

    def read_temp_raw(self, address):
        f = open(self.w1DeviceFolder + '/' + address + '/w1_slave', 'r')
        lines = f.readlines()
        f.close()
        return lines

    def get(self):
        lines = self.read_temp_raw(self.address)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw(self.address)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        return None

    def print_temperature(self, thermometer, data):
        print("[DS18b20]: %s => %s" % (thermometer, data))

    def test(self):
        thermometers = self.get_thermometers()
        for thermometer in thermometers:
            self.print_temperature(thermometer, self.read_temp(thermometer))


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
