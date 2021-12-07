import rpi_peripherals
import common
import log
import network_info
import time
import sensors

logger = log.get()
agregator_state = False
agregator_in_progress = False
agregator_step = 0
agregator_timestamp = 0
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

mqtt_messages = {
    "agregator_state": None,
    "agregator_in_progress": None,
    "agregator_step": None,
    "uptime": None,
    "ip": None,
    "temperature": None
}


def check_for_agregator_toggle():
    global agregator_state, agregator_in_progress
    if not agregator_in_progress:
        if agregator_state:
            agregator_state = False
            agregator_in_progress = True
        else:
            agregator_state = True
            agregator_in_progress = True


def on_button_state_change(state):
    logger.info("[LGC]: on_button_state_change %d" % (state))
    if state:
        check_for_agregator_toggle()


def blink_init_led():
    for i in range(3):
        rpi_peripherals.set_button_led(1)
        time.sleep(0.5)
        rpi_peripherals.set_button_led(0)
        time.sleep(0.5)


def init():
    logger.info("[LGC]: init begin")
    rpi_peripherals.init()
    rpi_peripherals.register_on_button_state_changed(on_button_state_change)
    global start_timestamp
    start_timestamp = common.get_millis()
    logger.info("[LGC]: init end")


def check_for_agregator_progress():
    global agregator_in_progress, agregator_step, agregator_timestamp
    if agregator_in_progress:
        if agregator_state:
            if agregator_step == 0:
                logger.info("[LGC]: agregator 0")
                agregator_timestamp = common.get_millis()
                rpi_peripherals.set_button_led(1)
                rpi_peripherals.set_relay(0, 1)
                agregator_step += 1
            elif agregator_step == 1 and common.millis_passed(agregator_timestamp) > 5000:
                logger.info("[LGC]: agregator 1")
                agregator_timestamp = common.get_millis()
                rpi_peripherals.set_relay(1, 1)
                agregator_step += 1
            elif agregator_step == 2 and common.millis_passed(agregator_timestamp) > 5000:
                logger.info("[LGC]: agregator 2")
                agregator_timestamp = common.get_millis()
                rpi_peripherals.set_relay(1, 0)
                rpi_peripherals.set_relay(2, 1)
                agregator_step += 1
            elif agregator_step == 3 and common.millis_passed(agregator_timestamp) > 5000:
                logger.info("[LGC]: agregator 3")
                agregator_timestamp = 0
                rpi_peripherals.set_relay(2, 0)
                agregator_in_progress = False
                agregator_step = 0
        if not agregator_state:
            rpi_peripherals.set_button_led(0)
            rpi_peripherals.set_relay(0, 0)
            agregator_in_progress = False


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
    if agregator_state != mqtt_messages["agregator_state"]:
        mqtt_messages["agregator_state"] = agregator_state
        return "agregator_state", int(agregator_state)
    if agregator_in_progress != mqtt_messages["agregator_in_progress"]:
        mqtt_messages["agregator_in_progress"] = agregator_in_progress
        return "agregator_in_progress", int(agregator_in_progress)
    if agregator_step != mqtt_messages["agregator_step"]:
        mqtt_messages["agregator_step"] = agregator_step
        return "agregator_step", agregator_step
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
    if topic == "agregator_toggle":
        check_for_agregator_toggle()


def get_uptime():
    return int(common.millis_passed(start_timestamp) / 1000)


def check_uptime():
    global uptime, uptime_check_timestamp
    if common.millis_passed(uptime_check_timestamp) >= 10000 or uptime_check_timestamp == 0:
        uptime_check_timestamp = common.get_millis()
        uptime = get_uptime()


def loop():
    rpi_peripherals.loop()
    check_for_agregator_progress()
    check_uptime()
    check_ip()


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
