import rpi_peripherals_havas as rpi_peripherals
import common
import log
import network_info

logger = log.get()


class Uptime:
    def __init__(self):
        self.timeout = 10000
        self.timestamp = 0
        self.mqtt = None
        self.mqtt_last = None
        self.name = "uptime"

    def init(self):
        self.timestamp = common.get_millis()

    def get(self):
        return int(common.millis_passed(self.timestamp) / 1000)

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


uptime = Uptime()
ip = Ip()


def init():
    logger.info("[LGC]: init begin")
    rpi_peripherals.init()
    uptime.init()
    ip.init()
    logger.info("[LGC]: init end")


def get_mqtt():
    if uptime.has_mqtt(): return uptime.get_mqtt()
    if ip.has_mqtt(): return ip.get_mqtt()
    return None, None


def set_mqtt(topic, message):
    logger.info("[LGC]: set_mqtt %s %s" % (topic, message))


def loop():
    uptime.loop()
    ip.loop()


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
