import os, sys

import rpi_peripherals_grijanje as rpi_peripherals
from logic_common import *

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from common import log

logger = log.get()

TEMPERATURE_INPUT_LIMIT = 29.0
TEMPERATURE_OUTPUT_LIMIT = 38.0
TEMPERATURE_RETURN_LIMIT = 0.0


class Temperature:
    def __init__(self, index, name):
        self.timeout = 10000
        self.timestamp = 0
        self.mqtt = None
        self.mqtt_last = None
        self.name = "temperature_" + name
        self.index = index
        self.temperature = None
        self.testing = False

    def init(self):
        pass

    def get(self):
        return self.temperature.get()

    def read(self):
        self.temperature = rpi_peripherals.temperature_sensors[self.index]

    def set(self, value):
        self.temperature = value
        self.mqtt = self.get()
        self.testing = True

    def loop(self):
        if common.millis_passed(self.timestamp) >= self.timeout or self.timestamp == 0:
            self.timestamp = common.get_millis()
            if not self.testing:
                self.read()
                self.mqtt = self.get()

    def has_mqtt(self):
        return self.mqtt != None and self.mqtt != self.mqtt_last

    def get_mqtt(self):
        if self.has_mqtt():
            self.mqtt_last = self.mqtt
            self.mqtt = None
            return self.name, self.mqtt_last
        return None, None


class Relay:
    def __init__(self, name, index):
        self.mqtt = None
        self.mqtt_last = None
        self.name = name
        self.index = index

    def init(self):
        pass

    def get(self):
        return rpi_peripherals.relays[self.index].get()

    def set(self, state):
        rpi_peripherals.relays[self.index].set(state)
        self.mqtt = state

    def loop(self):
        pass

    def has_mqtt(self):
        return self.mqtt != None and self.mqtt != self.mqtt_last

    def get_mqtt(self):
        if self.has_mqtt():
            self.mqtt_last = self.mqtt
            self.mqtt = None
            return self.name, self.mqtt_last
        return None, None

uptime = Uptime()
ip = Ip()
temperature_input = Temperature(0, "input")
temperature_output = Temperature(1, "output")
temperature_return = Temperature(2, "return")
temperature_input_limit = TemperatureLimit("input")
temperature_output_limit = TemperatureLimit("output")
temperature_return_limit = TemperatureLimit("return")
pump = Relay("pump", 0)
automatic = Automatic()


def init():
    logger.info("[LGC]: init begin")
    global init_status
    rpi_peripherals.init()
    uptime.init()
    ip.init()
    temperature_input.init()
    temperature_output.init()
    temperature_return.init()
    temperature_input_limit.init()
    temperature_output_limit.init()
    temperature_return_limit.init()
    temperature_input_limit.set(TEMPERATURE_INPUT_LIMIT)
    temperature_output_limit.set(TEMPERATURE_OUTPUT_LIMIT)
    temperature_return_limit.set(TEMPERATURE_RETURN_LIMIT)
    pump.init()
    automatic.init()
    logger.info("[LGC]: init end")


def get_mqtt():
    if uptime.has_mqtt(): return uptime.get_mqtt()
    if ip.has_mqtt(): return ip.get_mqtt()
    if temperature_input.has_mqtt(): return temperature_input.get_mqtt()
    if temperature_output.has_mqtt(): return temperature_output.get_mqtt()
    if temperature_return.has_mqtt(): return temperature_return.get_mqtt()
    if temperature_input_limit.has_mqtt(): return temperature_input_limit.get_mqtt()
    if temperature_output_limit.has_mqtt(): return temperature_output_limit.get_mqtt()
    if temperature_return_limit.has_mqtt(): return temperature_return_limit.get_mqtt()
    if pump.has_mqtt(): return pump.get_mqtt()
    if automatic.has_mqtt(): return automatic.get_mqtt()
    return None, None


def set_mqtt(topic, message):
    logger.info("[LGC]: set_mqtt %s %s" % (topic, message))
    if topic == pump.name:
        if not automatic.get():
            pump.set(int(message))
    elif topic == automatic.name:
        automatic.set(int(message))
    elif topic == temperature_input.name:
        temperature_input.set(float(message))
    elif topic == temperature_output.name:
        temperature_output.set(float(message))
    elif topic == temperature_return.name:
        temperature_return.set(float(message))
    elif topic == temperature_input_limit.name:
        temperature_input_limit.set(float(message))
    elif topic == temperature_output_limit.name:
        temperature_output_limit.set(float(message))
    elif topic == temperature_return_limit.name:
        temperature_return_limit.set(float(message))


def check_for_automatisation():
    if automatic.get() and temperature_input.get() != None and temperature_output.get() != None:
        if pump.get():
            if temperature_input.get() < temperature_input_limit.get() or \
                    temperature_output.get() > temperature_output_limit.get():
                pump.set(0)
        else:
            if temperature_input.get() >= temperature_input_limit.get() and \
                    temperature_output.get() <= temperature_output_limit.get():
                pump.set(1)


def loop_unblocking():
    uptime.loop()
    ip.loop()
    pump.loop()
    automatic.loop()
    temperature_input_limit.loop()
    temperature_output_limit.loop()
    temperature_return_limit.loop()
    check_for_automatisation()


def loop_blocking():
    temperature_input.loop()
    temperature_output.loop()
    temperature_return.loop()


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
