import os, sys

import rpi_peripherals_ssc_powermeter as rpi_peripherals
from logic_common import *

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from common import log

logger = log.get()


class PowerMeasurement:
    def __init__(self):
        self.timeout = 10000
        self.timestamp = 0
        self.start_timestamp = 0
        self.mqtt = {}
        self.name = "power_measurement"

    def init(self):
        pass

    def get(self):
        return rpi_peripherals.get_power_measurement()

    def loop(self):
        if common.millis_passed(self.timestamp) >= self.timeout or self.timestamp == 0:
            self.timestamp = common.get_millis()
            self.mqtt = self.get()
            print(self.mqtt)

    def has_mqtt(self):
        return len(self.mqtt.items()) > 0

    def get_mqtt(self):
        if self.has_mqtt():
            key = list(self.mqtt.keys())[0]
            value = self.mqtt.pop(key)
            return f"{self.name}/{key}", value
        return None, None


uptime = Uptime()
ip = Ip()
power_measurement = PowerMeasurement()


def init():
    logger.info("[LGC]: init begin")
    global init_status
    rpi_peripherals.init()
    uptime.init()
    ip.init()
    power_measurement.init()
    logger.info("[LGC]: init end")


def get_mqtt():
    if uptime.has_mqtt(): return uptime.get_mqtt()
    if ip.has_mqtt(): return ip.get_mqtt()
    if power_measurement.has_mqtt(): return power_measurement.get_mqtt()
    return None, None


def set_mqtt(topic, message):
    logger.info("[LGC]: set_mqtt %s %s" % (topic, message))


def loop_unblocking():
    uptime.loop()
    ip.loop()
    power_measurement.loop()


def loop_blocking():
    pass


def loop_test():
    init()
    while True:
        loop_unblocking()
        loop_blocking()


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
