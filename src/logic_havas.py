import rpi_peripherals_havas as rpi_peripherals
import common
import log
import network_info

logger = log.get()

TEMPERATURE_INPUT_LIMIT = 40.0
TEMPERATURE_OUTPUT_LIMIT = 30.0
TEMPERATURE_RETURN_LIMIT = 20.0


class Uptime:
    def __init__(self):
        self.timeout = 10000
        self.timestamp = 0
        self.start_timestamp = 0
        self.mqtt = None
        self.mqtt_last = None
        self.name = "uptime"

    def init(self):
        self.start_timestamp = common.get_millis()

    def get(self):
        return int(common.millis_passed(self.start_timestamp) / 1000)

    def loop(self):
        if common.millis_passed(self.timestamp) >= 10000 or self.timestamp == 0:
            self.timestamp = common.get_millis()
            self.mqtt = self.get()

    def has_mqtt(self):
        return self.mqtt != None and self.mqtt != self.mqtt_last

    def get_mqtt(self):
        if self.has_mqtt():
            self.mqtt_last = self.mqtt
            self.mqtt = None
            return self.name, self.mqtt_last
        return None, None


class Ip:
    def __init__(self):
        self.timeout = 30000
        self.timestamp = 0
        self.mqtt = None
        self.mqtt_last = None
        self.name = "ip"
        self.usb_ip = None
        self.wlan_ip = None
        self.vpn_ip = None

    def init(self):
        pass

    def loop(self):
        if common.millis_passed(self.timestamp) >= 10000 or self.timestamp == 0:
            self.timestamp = common.get_millis()
            new_usb_ip = network_info.get_ip_from_usb()
            if new_usb_ip != None:
                self.usb_ip = new_usb_ip
            new_wlan_ip = network_info.get_ip_from_wifi()
            if new_wlan_ip != None:
                self.wlan_ip = new_wlan_ip
            new_vpn_ip = network_info.get_ip_from_vpn()
            if new_vpn_ip != None:
                self.vpn_ip = new_vpn_ip
            str_ip = ""
            str_ip += "u: %s\n" % (str(self.usb_ip))
            str_ip += "w: %s\n" % (str(self.wlan_ip))
            str_ip += "t: %s\n" % (str(self.vpn_ip))
            self.mqtt = str_ip

    def has_mqtt(self):
        return self.mqtt != None and self.mqtt != self.mqtt_last

    def get_mqtt(self):
        if self.has_mqtt():
            self.mqtt_last = self.mqtt
            self.mqtt = None
            return self.name, self.mqtt_last
        return None, None


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
        return self.temperature

    def read(self):
        self.temperature = rpi_peripherals.get_temperature(self.index)

    def set(self, value):
        self.temperature = value
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


class TemperatureLimit:
    def __init__(self, name):
        self.mqtt = None
        self.mqtt_last = None
        self.name = "temperature_" + name + "_limit"
        self.temperature = None

    def init(self):
        pass

    def get(self):
        return self.temperature

    def set(self, value):
        self.temperature = value
        self.mqtt = self.temperature

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


class Pump:
    def __init__(self):
        self.mqtt = None
        self.mqtt_last = None
        self.name = "pump"

    def init(self):
        pass

    def get(self):
        return rpi_peripherals.get_relay_state()

    def set(self, state):
        rpi_peripherals.set_relay(state)
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


class Automatic:
    def __init__(self):
        self.timeout = 10000
        self.timestamp = 0
        self.mqtt = None
        self.mqtt_last = None
        self.name = "automatic"
        self.state = None

    def init(self):
        self.set(True)

    def get(self):
        return int(self.state)

    def set(self, state):
        self.state = int(state)
        self.mqtt = self.state

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
pump = Pump()
automatic = Automatic()


def init():
    logger.info("[LGC]: init begin")
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
