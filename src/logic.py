import rpi_peripherals
import common
import log

logger = log.get()
agregator_state = False
agregator_in_progress = False


def on_button_state_change(state):
    logger.info("[LGC]: on_button_state_change %d" % (state))
    global agregator_state, agregator_in_progress
    if not agregator_state and not agregator_in_progress:
        agregator_state = True
        agregator_in_progress = True
    if agregator_state and not agregator_in_progress:
        agregator_state = False
        agregator_in_progress = True


def init():
    logger.info("[LGC]: init begin")
    rpi_peripherals.init()
    rpi_peripherals.register_on_button_state_changed(on_button_state_change)
    logger.info("[LGC]: init end")


def check_for_agregator():
    global agregator_in_progress
    if agregator_state and agregator_in_progress:
        rpi_peripherals.set_button_led(1)
        rpi_peripherals.set_relay(0, 1)
        agregator_in_progress = False
    if not agregator_state and agregator_in_progress:
        rpi_peripherals.set_button_led(0)
        rpi_peripherals.set_relay(0, 0)
        agregator_in_progress = False


def loop():
    rpi_peripherals.loop()


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
