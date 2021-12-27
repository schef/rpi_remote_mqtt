import os, sys
import network_info

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common import common


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
