import os, sys

from credentials import test

if not test:
    from periphery import GPIO

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common import log

logger = log.get()

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

BUTTON_UP = 23
BUTTON_DOWN = 24
RELAY_UP = 15
RELAY_DOWN = 14

buttons = []
relays = []
on_button_state_changed = None


class Relay:
    def __init__(self, name, pin=None, inverted=True):
        self.name = name
        self.output = None
        self.inverted = inverted
        if pin is not None:
            self.output = GPIO("/dev/gpiochip0", pin, "out", inverted=inverted)
        self.state = None

    def set_state(self, state):
        logger.debug("[RPI] set_state[%s,%d]" % (self.name, state))
        if self.output is not None:
            self.output.write(bool(state))
            self.state = state

    def get_state(self):
        return self.state


class Button:
    def __init__(self, name, pin=None, inverted=True):
        self.name = name
        self.input = None
        if pin is not None:
            self.input = GPIO("/dev/gpiochip0", pin, "in", bias="pull_up", inverted=inverted)
        self.state = None

    def get_new_state(self):
        if self.input is not None:
            state = int(self.input.read())
            if state != self.state:
                self.state = state
                logger.debug("[RPI] get_new_state[%s,%d]" % (self.name, self.state))
                return self.state
        return None

    def get_last_state(self):
        return self.state


def init():
    logger.info("[RPI]: init begin")
    global buttons, relays
    if test:
        buttons.append(Button("BUTTON_UP"))
        buttons.append(Button("BUTTON_DOWN"))
        relays.append(Relay("RELAY_UP"))
        relays.append(Relay("RELAY_DOWN"))
    else:
        buttons.append(Button("BUTTON_UP", BUTTON_UP))
        buttons.append(Button("BUTTON_DOWN", BUTTON_DOWN))
        relays.append(Relay("RELAY_UP", RELAY_UP))
        relays.append(Relay("RELAY_DOWN", RELAY_DOWN))
    for relay in relays:
        relay.set_state(0)
    logger.info("[RPI]: init end")


def check_button_state():
    for button in buttons:
        state = button.get_new_state()
        if state is not None:
            if on_button_state_changed is not None:
                on_button_state_changed(button.name, button.state)


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
