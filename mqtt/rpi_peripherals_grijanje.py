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

RELAY_0 = 23
relay = None
relay_state = None

TEMP_0 = '28-051684308bff'
TEMP_1 = '28-0516843330ff'
TEMP_2 = '28-051684344cff'


class TestRelay:
    def write(self, state):
        logger.debug("TestRelay.write %s" % (str(state)))


def set_relay(state):
    global relay_state
    relay.write(bool(state))
    relay_state = state


def get_relay_state():
    return relay_state


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
    global relay
    if test:
        relay = TestRelay()
    else:
        relay = GPIO("/dev/gpiochip0", RELAY_0, "out")
    set_relay(False)
    logger.info("[RPI]: init end")


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
