import os, sys

from periphery import GPIO
from credentials import test

if test:
    pass
else:
    import ds18b20

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common import log

logger = log.get()

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

RELAY_PINS = [23, 24, 25, 8]
relays = []

TEMP_0 = '28-0516843756ff'


class GPIOTest:
    def __init__(self, pin):
        self.pin = pin

    def write(self, state):
        logger.debug(f"TestRelay[{self.pin}].write {state}")


class Relay:
    def __init__(self, pin: int):
        if test:
            self.relay = GPIOTest(pin)
        else:
            self.relay = GPIO("/dev/gpiochip0", pin, "out")
        self.state = None

    def set(self, state):
        self.relay.write(bool(state))
        self.state = state

    def get(self):
        return self.state


def get_temperature(num):
    if test:
        return 23.456
    else:
        try:
            if num == 0:
                return ds18b20.read_temp(TEMP_0)
            elif num == 1:
                return ds18b20.read_temp(TEMP_1)
            elif num == 2:
                return ds18b20.read_temp(TEMP_2)
        except:
            return None


def init():
    logger.info("[RPI]: init begin")
    for pin in RELAY_PINS:
        relays.append(Relay(pin))
        relays[-1].set(False)
    logger.info("[RPI]: init end")


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
