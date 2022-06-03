import rpi_peripherals_rmale as rpi_peripherals
from logic_common import *

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common import log, common

logger = log.get()


class ThingInt:
    def __init__(self, name):
        self.mqtt = None
        self.mqtt_last = None
        self.name = name
        self.value = None

    def get(self):
        return int(self.value)

    def set(self, value):
        self.value = value
        self.mqtt = self.value

    def has_mqtt(self):
        return self.mqtt != None and self.mqtt != self.mqtt_last

    def get_mqtt(self):
        if self.has_mqtt():
            self.mqtt_last = self.mqtt
            self.mqtt = None
            return self.name, self.mqtt_last
        return None, None


class RolloSingleDirection:
    def __init__(self, relay, button):
        self.relay = relay
        self.button = button
        self.active = False


class Rollo:
    def __init__(self, path, rollo_up, rollo_down):
        self.path = path
        self.up = rollo_up
        self.down = rollo_down
        self.timestamp = None
        self.max_timeout = 25000
        self.timeout = self.max_timeout
        self.current_position = None
        self.first_time_position = None


rollos = {
    "rollo/1": Rollo("rollo/1", RolloSingleDirection("RELAY_UP", "BUTTON_UP"), RolloSingleDirection("RELAY_DOWN", "BUTTON_DOWN")),
}

uptime = Uptime()
ip = Ip()
rollo_percent = ThingInt("rollo/1")

mqtt_messages = {
    "voltage": None
}


def on_button_state_change(name, state):
    logger.info("[LGC]: on_button_state_change[%s,%d]" % (name, state))
    check_rollos_for_button(name, state)


def init():
    logger.info("[LGC]: init begin")
    rpi_peripherals.init()
    rpi_peripherals.register_on_button_state_changed(on_button_state_change)
    uptime.init()
    ip.init()
    logger.info("[LGC]: init end")


def get_percent_from_data(data):
    if data == "UP":
        return 100
    elif data == "DOWN":
        return 0
    else:
        try:
            percent = int(data)
            if percent >= 0 and percent <= 100:
                return percent
        except Exception as e:
            print("[PHY]: ERROR: with error %s" % (e))
    return None


def get_rollo_from_alias(alias) -> Rollo:
    rollo = None
    for key in rollos:
        if alias == rollos[key].up.button or alias == rollos[key].down.button:
            rollo = rollos[key]
    return rollo


def check_rollos_for_button(name, state):
    rollo = get_rollo_from_alias(name)
    if rollo is not None:
        if int(state) == 0:
            if rollo.up.active or rollo.down.active:
                set_rollos(rollo, "STOP")
            else:
                if rollo.up.button == name:
                    set_rollos(rollo, "UP")
                elif rollo.down.button == name:
                    set_rollos(rollo, "DOWN")


def set_rollos(rollo, data):
    print("[LGC]: set_rollos[%s], data[%s]" % (rollo.path, data))
    if data == "STOP":
        rpi_peripherals.relays[0].set_state(0)
        if rollo.up.active:
            if common.millis_passed(rollo.timestamp) >= rollo.max_timeout:
                rollo.current_position = 100
            else:
                if rollo.current_position is not None:
                    rollo.current_position = rollo.current_position + int(common.millis_passed(rollo.timestamp) / rollo.max_timeout * 100)
                    if rollo.current_position > 100:
                        rollo.current_position = 100
        elif rollo.down.active:
            if common.millis_passed(rollo.timestamp) >= rollo.max_timeout:
                rollo.current_position = 0
            else:
                if rollo.current_position is not None:
                    rollo.current_position = rollo.current_position - int(common.millis_passed(rollo.timestamp) / rollo.max_timeout * 100)
                    if rollo.current_position < 0:
                        rollo.current_position = 0
        print("[LGC]: rollo[%s], position[%s]" % (rollo.path, str(rollo.current_position)))
        rollo_percent.set(rollo.current_position)
        rollo.up.active = False
        rpi_peripherals.relays[1].set_state(0)
        rollo.down.active = False
        rollo.timeout = None
        rollo.timestamp = None
    else:
        percent = get_percent_from_data(data)
        if percent is not None:
            direction_up = False
            direction_down = False
            timeout = None
            if percent == 100:
                direction_up = True
                timeout = rollo.max_timeout
            elif percent == 0:
                direction_down = True
                timeout = rollo.max_timeout
            else:
                if rollo.current_position is not None:
                    move_percent = percent - rollo.current_position
                    timeout = abs(int(move_percent / 100 * rollo.max_timeout))
                    if move_percent > 0:
                        direction_up = True
                    elif move_percent < 0:
                        direction_down = True
                else:
                    rollo.first_time_position = percent
                    direction_up = True
                    timeout = rollo.max_timeout
            if direction_up:
                if rollo.down.active:
                    rpi_peripherals.relays[1].set_state(0)
                    rollo.down.active = False
                rpi_peripherals.relays[0].set_state(1)
                rollo.up.active = True
                rollo.timeout = timeout
                rollo.timestamp = common.get_millis()
            elif direction_down:
                if rollo.up.active:
                    rpi_peripherals.relays[0].set_state(0)
                    rollo.up.active = False
                rpi_peripherals.relays[1].set_state(1)
                rollo.down.active = True
                rollo.timeout = timeout
                rollo.timestamp = common.get_millis()


def check_rollos_timeout():
    for key in rollos:
        rollo = rollos[key]
        if rollo.up.active or rollo.down.active:
            if common.millis_passed(rollo.timestamp) >= rollo.timeout:
                set_rollos(rollo, "STOP")
                if rollo.first_time_position is not None:
                    if rollo.current_position is None:
                        rollo.first_time_position = None
                    else:
                        set_rollos(rollo, rollo.first_time_position)
                        rollo.first_time_position = None


def get_mqtt():
    if uptime.has_mqtt(): return uptime.get_mqtt()
    if ip.has_mqtt(): return ip.get_mqtt()
    if rollo_percent.has_mqtt(): return rollo_percent.get_mqtt()
    return None, None


def set_mqtt(topic, message):
    logger.info("[LGC]: set_mqtt %s %s" % (topic, message))
    rollo = rollos.get(topic)
    if rollo is not None:
        set_rollos(rollo, message)


def loop_unblocking():
    rpi_peripherals.loop()
    uptime.loop()
    ip.loop()
    check_rollos_timeout()


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
