import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from rpi_peripherals_common import Relay, TemperatureSensor
from credentials import test

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

RELAY_PINS = [23]
relays = []
TEMPERATURE_ADDRESSES = ['28-051684308bff', '28-0516843330ff', '28-051684344cff']
temperature_sensors = []


def init():
    print("[RPI]: init begin")
    for pin in RELAY_PINS:
        relays.append(Relay(pin, invert=False, test=test))
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
