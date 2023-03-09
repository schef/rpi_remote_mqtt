import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from rpi_peripherals_common import Relay, TemperatureSensor
from credentials import test

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

RELAY_PINS = [23, 24, 25, 8]
relays = []
TEMPERATURE_ADDRESSES = ['28-0516843756ff', '28-3c71f6494dd2']
temperature_sensors = []


def init():
    print("[RPI]: init begin")
    for pin in RELAY_PINS:
        relays.append(Relay(pin, invert=True, test=test))
        relays[-1].set(False)
    for address in TEMPERATURE_ADDRESSES:
        temperature_sensors.append(TemperatureSensor(address, test=test))
    print("[RPI]: init end")


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
