import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from rpi_peripherals_common import PM5100
from credentials import test

meter = None


def init():
    print("[RPI]: init begin")
    print("[RPI]: init end")


def get_power_measurement():
    global meter
    if meter == None:
        try:
            # TODO: find tty name by PID and VID or USB port
            meter = PM5100(tty="/dev/ttyUSB0", test=test)
            return meter.get()
        except Exception as e:
            print(f"[METER]: Error with {e}")
            return {}
    else:
        try:
            return meter.get()
        except Exception as e:
            print(f"[METER]: Error with {e}")
            return {}


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
