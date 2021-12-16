import rpi_peripherals_generic as rpi_peripherals
import common
import log
import network_info
import sensors

logger = log.get()
start_timestamp = 0
uptime = 0
uptime_check_timestamp = 0
ip_check_timestamp = 0
usb_ip = None
wlan_ip = None
vpn_ip = None
ip = None
temperature = None
temperature_check_timestamp = 0
internet_timestamp = 0

init_status = False
internet_status = False

mqtt_messages = {
    "uptime": None,
    "ip": None,
    "temperature": None
}


def on_button_state_change(state):
    logger.info("[LGC]: on_button_state_change %d" % (state))


def check_for_internet():
    global internet_timestamp, internet_status
    if common.millis_passed(internet_timestamp) >= 10000 or internet_timestamp == 0:
        internet_timestamp = common.get_millis()
        ip = network_info.get_public_ip()
        if ip:
            if internet_status == False:
                internet_status = True
        else:
            if internet_status == True:
                internet_status = False


def init():
    global init_status
    logger.info("[LGC]: init begin")
    rpi_peripherals.init()
    rpi_peripherals.register_on_button_state_changed(on_button_state_change)
    global start_timestamp
    start_timestamp = common.get_millis()
    init_status = True
    logger.info("[LGC]: init end")


def check_ip():
    global ip_check_timestamp, usb_ip, vpn_ip, wlan_ip, ip
    if common.millis_passed(ip_check_timestamp) >= 30000 or ip_check_timestamp == 0:
        ip_check_timestamp = common.get_millis()
        new_usb_ip = network_info.get_ip_from_usb()
        if new_usb_ip != None:
            usb_ip = new_usb_ip
        new_wlan_ip = network_info.get_ip_from_wifi()
        if new_wlan_ip != None:
            wlan_ip = new_wlan_ip
        new_vpn_ip = network_info.get_ip_from_vpn()
        if new_vpn_ip != None:
            vpn_ip = new_vpn_ip
        str_ip = ""
        str_ip += "usb0: %s\n" % (str(usb_ip))
        str_ip += "wlan0: %s\n" % (str(wlan_ip))
        str_ip += "tun0: %s\n" % (str(vpn_ip))
        ip = str_ip


def check_temperature():
    global temperature, temperature_check_timestamp
    if common.millis_passed(temperature_check_timestamp) >= 60000 or temperature_check_timestamp == 0:
        temperature_check_timestamp = common.get_millis()
        new_temp = sensors.get_temperature()
        if new_temp != None:
            temperature = new_temp


def get_mqtt():
    if uptime != mqtt_messages["uptime"]:
        mqtt_messages["uptime"] = uptime
        return "uptime", uptime
    if ip != mqtt_messages["ip"]:
        mqtt_messages["ip"] = ip
        return "ip", ip
    if temperature != mqtt_messages["temperature"]:
        mqtt_messages["temperature"] = temperature
        return "temperature", temperature
    return None, None


def set_mqtt(topic, message):
    logger.info("[LGC]: set_mqtt %s %s" % (topic, message))


def get_uptime():
    return int(common.millis_passed(start_timestamp) / 1000)


def check_uptime():
    global uptime, uptime_check_timestamp
    if common.millis_passed(uptime_check_timestamp) >= 10000 or uptime_check_timestamp == 0:
        uptime_check_timestamp = common.get_millis()
        uptime = get_uptime()


def loop():
    rpi_peripherals.loop()
    check_uptime()
    check_ip()
    # check_for_internet()


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