import os, sys

from credentials import test

if test:
    pass
else:
    from periphery import GPIO, I2C
    import ina219

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common import log

logger = log.get()

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

BUTTON_LED = 12
BUTTON_IN = 16
RELAY_0 = 18
RELAY_1 = 23
RELAY_2 = 24
RELAY_3 = 25
SHUNT_OHMS = 0.1

button_led = None
button_in = None
relays = []
i2c = None
ina = None
button_state = None
on_button_state_changed = None
button_led_state = None


# i2cdetect -y 1

class TestRelay:
    def __init__(self, name):
        self.name = name

    def write(self, state):
        logger.debug("%s.write %s" % (self.name, str(state)))

    def read(self):
        return 1


def set_button_led(state):
    global button_led_state
    button_led_state = bool(state)
    button_led.write(bool(state))


def get_button_led_state():
    return button_led_state


def get_button_state():
    return int(button_in.read())


def set_relay(num, state):
    relays[num].write(bool(state))


def ina_get_measure():
    voltage = ina.voltage()
    current = ina.current()
    power = ina.power()
    print("Bus Voltage: %.3f V" % voltage)
    print("Current: %.3f mA" % current)
    print("Power: %.3f mW" % power)
    return (voltage, current, power)


def init():
    logger.info("[RPI]: init begin")
    global button_led, button_in, relays, i2c, ina
    if test:
        button_led = TestRelay("BUTTON_LED")
        button_in = TestRelay("BUTTON_IN")
        relays.append(TestRelay("RELAY_0"))
        relays.append(TestRelay("RELAY_1"))
        relays.append(TestRelay("RELAY_2"))
        relays.append(TestRelay("RELAY_3"))
    else:
        button_led = GPIO("/dev/gpiochip0", BUTTON_LED, "out")
        button_in = GPIO("/dev/gpiochip0", BUTTON_IN, "in", bias="pull_up", inverted=True)
        relays.append(GPIO("/dev/gpiochip0", RELAY_0, "out"))
        relays.append(GPIO("/dev/gpiochip0", RELAY_1, "out"))
        relays.append(GPIO("/dev/gpiochip0", RELAY_2, "out"))
        relays.append(GPIO("/dev/gpiochip0", RELAY_3, "out"))
    set_button_led(False)
    for i in range(len(relays)):
        set_relay(i, False)
    # i2c = I2C("/dev/i2c-1")
    # ina = ina219.INA219(SHUNT_OHMS, i2c)
    # ina.configure()
    logger.info("[RPI]: init end")


def check_button_state():
    global button_state
    current_state = get_button_state()
    if current_state != button_state:
        button_state = current_state
        logger.info("[RPI]: button state changed %d" % (button_state))
        if on_button_state_changed:
            on_button_state_changed(button_state)


def register_on_button_state_changed(func):
    global on_button_state_changed
    on_button_state_changed = func


def loop():
    check_button_state()


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
