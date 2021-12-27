import os, sys

import network_info
import rpi_peripherals_ekofarma as rpi_peripherals
import led_logic
from logic_common import *

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common import log, common

logger = log.get()


class ThingBool:
    def __init__(self, name):
        self.mqtt = None
        self.mqtt_last = None
        self.name = name
        self.state = False

    def init(self):
        self.mqtt = int(self.state)

    def get(self):
        return int(self.state)

    def set(self, state):
        self.state = state
        self.mqtt = int(self.state)

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


class ThingInt:
    def __init__(self, name):
        self.mqtt = None
        self.mqtt_last = None
        self.name = name
        self.value = 0

    def init(self):
        self.mqtt = int(self.value)

    def get(self):
        return int(self.value)

    def set(self, value):
        self.value = value
        self.mqtt = int(self.value)

    def increment(self, value):
        new = self.get() + value
        self.set(new)

    def decrement(self, value):
        new = self.get() - value
        self.set(new)

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
agregator_state = ThingBool("agregator_state")
agregator_in_progress = ThingBool("agregator_in_progress")
agregator_step = ThingInt("agregator_step")
agregator_timestamp = 0

voltage = None
voltage_timestamp = 0

mqtt_messages = {
    "voltage": None
}


def check_for_agregator_toggle():
    if not agregator_in_progress.get():
        if agregator_state.get():
            agregator_state.set(False)
            agregator_in_progress.set(True)
        else:
            agregator_state.set(True)
            agregator_in_progress.set(True)


def on_button_state_change(state):
    logger.info("[LGC]: on_button_state_change %d" % (state))
    if state:
        check_for_agregator_toggle()


def update_led():
    led_logic.set_led(1, agregator_state.get())


def check_for_voltage():
    global voltage, voltage_timestamp
    if common.millis_passed(voltage_timestamp) >= 60000 or voltage_timestamp == 0:
        voltage_timestamp = common.get_millis()
        voltage = rpi_peripherals.ina.voltage()


def init():
    logger.info("[LGC]: init begin")
    rpi_peripherals.init()
    rpi_peripherals.register_on_button_state_changed(on_button_state_change)
    uptime.init()
    ip.init()
    agregator_state.init()
    agregator_in_progress.init()
    agregator_step.init()
    update_led()
    logger.info("[LGC]: init end")


def check_for_agregator_progress():
    global agregator_timestamp
    if agregator_in_progress.get():
        if agregator_state.get():
            if agregator_step.get() == 0:
                logger.info("[LGC]: agregator 0")
                agregator_timestamp = common.get_millis()
                update_led()
                rpi_peripherals.set_relay(0, 1)
                agregator_step.increment(1)
            elif agregator_step.get() == 1 and common.millis_passed(agregator_timestamp) > 30000:
                logger.info("[LGC]: agregator 1")
                agregator_timestamp = common.get_millis()
                rpi_peripherals.set_relay(1, 1)
                agregator_step.increment(1)
            elif agregator_step.get() == 2 and common.millis_passed(agregator_timestamp) > 2000:
                logger.info("[LGC]: agregator 2")
                agregator_timestamp = common.get_millis()
                rpi_peripherals.set_relay(1, 0)
                agregator_step.increment(1)
            elif agregator_step.get() == 3 and common.millis_passed(agregator_timestamp) > 10000:
                logger.info("[LGC]: agregator 3")
                agregator_timestamp = common.get_millis()
                rpi_peripherals.set_relay(2, 1)
                agregator_step.increment(1)
            elif agregator_step.get() == 4 and common.millis_passed(agregator_timestamp) > 10000:
                logger.info("[LGC]: agregator 4")
                agregator_timestamp = 0
                rpi_peripherals.set_relay(2, 0)
                agregator_in_progress.set(False)
                agregator_step.set(0)
        if not agregator_state.get():
            update_led()
            rpi_peripherals.set_relay(0, 0)
            agregator_in_progress.set(False)


def get_mqtt():
    if uptime.has_mqtt(): return uptime.get_mqtt()
    if ip.has_mqtt(): return ip.get_mqtt()
    if agregator_state.has_mqtt(): return agregator_state.get_mqtt()
    if agregator_in_progress.has_mqtt(): return agregator_in_progress.get_mqtt()
    if agregator_step.has_mqtt(): return agregator_step.get_mqtt()
    if voltage != mqtt_messages["voltage"]:
        mqtt_messages["voltage"] = voltage
        return "voltage", voltage
    return None, None


def set_mqtt(topic, message):
    logger.info("[LGC]: set_mqtt %s %s" % (topic, message))
    if topic == "agregator_toggle":
        check_for_agregator_toggle()


def loop_unblocking():
    rpi_peripherals.loop()
    uptime.loop()
    ip.loop()
    agregator_state.loop()
    agregator_in_progress.loop()
    agregator_step.loop()
    check_for_agregator_progress()
    led_logic.loop()


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
