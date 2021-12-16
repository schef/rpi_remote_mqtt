from periphery import GPIO
import log
import ds18b20

logger = log.get()

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

RELAY_0 = 23
relay = None

TEMP_0 = '28-051684344cff'
TEMP_1 = '28-0516843330ff'
TEMP_2 = '28-051684308bff'

def set_relay(state):
    relay.write(bool(state))


def init():
    logger.info("[RPI]: init begin")
    global relay
    relay = GPIO("/dev/gpiochip0", RELAY_0, "out")
    set_relay(False)
    logger.info("[RPI]: init end")


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
