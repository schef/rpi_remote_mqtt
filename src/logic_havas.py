import rpi_peripherals_havas as rpi_peripherals
import common
import log
import network_info

logger = log.get()


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
    def __init__(self):
        self.timeout = 10000
        self.timestamp = 0
        self.mqtt = None
        self.mqtt_last = None
        self.name = "temperature"
        self.t0 = None
        self.t1 = None
        self.t2 = None
        self.count = 0

    def init(self):
        pass

    def generate_message(self):
        mstr = ""
        mstr += "t0: %s\n" % (str(self.t0))
        mstr += "t1: %s\n" % (str(self.t1))
        mstr += "t2: %s\n" % (str(self.t2))
        return mstr

    def get(self, num):
        if num == 0:
            return self.t0
        elif num == 1:
            return self.t1
        elif num == 2:
            return self.t2
        return None

    def loop(self):
        if common.millis_passed(self.timestamp) >= 5000 or self.timestamp == 0:
            self.timestamp = common.get_millis()
            if self.count == 0:
                self.t0 = rpi_peripherals.get_temperature(0)
            elif self.count == 1:
                self.t1 = rpi_peripherals.get_temperature(1)
            elif self.count == 2:
                self.t2 = rpi_peripherals.get_temperature(2)
            self.count += 1
            if self.count >= 3:
                self.count = 0
            self.mqtt = self.generate_message()

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
temperature = Temperature()
pump = Pump()
automatic = Automatic()


def init():
    logger.info("[LGC]: init begin")
    rpi_peripherals.init()
    uptime.init()
    ip.init()
    temperature.init()
    pump.init()
    automatic.init()
    logger.info("[LGC]: init end")


def get_mqtt():
    if uptime.has_mqtt(): return uptime.get_mqtt()
    if ip.has_mqtt(): return ip.get_mqtt()
    if temperature.has_mqtt(): return temperature.get_mqtt()
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


def loop():
    uptime.loop()
    ip.loop()
    temperature.loop()
    pump.loop()
    automatic.loop()


def loop_test():
    init()
    while True:
        loop()


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
