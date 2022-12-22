import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from rpi_peripherals_common import Relay, PowerMeasurement
from credentials import test

RELAY_PINS = [23, 24, 25, 8]
relays = []
meters = []


def init():
    print("[RPI]: init begin")
    for pin in RELAY_PINS:
        relays.append(Relay(pin, invert=True, test=test))
        relays[-1].set(False)
    meters.append(PowerMeasurement(tty="/dev/ttyUSB"))
    print("[RPI]: init end")


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
