import rpi_peripherals
import common
import log

logger = log.get()
agregator_state = False
agregator_in_progress = False
agregator_step = 0
timestamp = 0

mqtt_messages = {
    "agregator_state": None,
    "agregator_in_progress": None,
    "agregator_step": None,
}


def check_for_agregator_toggle():
    global agregator_state, agregator_in_progress
    if not agregator_in_progress:
        if agregator_state:
            agregator_state = False
            agregator_in_progress = True
        else:
            agregator_state = True
            agregator_in_progress = True


def on_button_state_change(state):
    logger.info("[LGC]: on_button_state_change %d" % (state))
    if state:
        check_for_agregator_toggle()


def init():
    logger.info("[LGC]: init begin")
    rpi_peripherals.init()
    rpi_peripherals.register_on_button_state_changed(on_button_state_change)
    logger.info("[LGC]: init end")


def check_for_agregator_progress():
    global agregator_in_progress, agregator_step, timestamp
    if agregator_in_progress:
        if agregator_state:
            if agregator_step == 0:
                logger.info("[LGC]: agregator 0")
                timestamp = common.get_millis()
                rpi_peripherals.set_button_led(1)
                rpi_peripherals.set_relay(0, 1)
                agregator_step += 1
            elif agregator_step == 1 and common.millis_passed(timestamp) > 5000:
                logger.info("[LGC]: agregator 1")
                timestamp = common.get_millis()
                rpi_peripherals.set_relay(1, 1)
                agregator_step += 1
            elif agregator_step == 2 and common.millis_passed(timestamp) > 5000:
                logger.info("[LGC]: agregator 2")
                timestamp = common.get_millis()
                rpi_peripherals.set_relay(1, 0)
                rpi_peripherals.set_relay(2, 1)
                agregator_step += 1
            elif agregator_step == 3 and common.millis_passed(timestamp) > 5000:
                logger.info("[LGC]: agregator 3")
                timestamp = 0
                rpi_peripherals.set_relay(2, 0)
                agregator_in_progress = False
                agregator_step = 0
        if not agregator_state:
            rpi_peripherals.set_button_led(0)
            rpi_peripherals.set_relay(0, 0)
            agregator_in_progress = False


def get_mqtt():
    if agregator_state != mqtt_messages["agregator_state"]:
        mqtt_messages["agregator_state"] = agregator_state
        return "agregator_state", int(agregator_state)
    if agregator_in_progress != mqtt_messages["agregator_in_progress"]:
        mqtt_messages["agregator_in_progress"] = agregator_in_progress
        return "agregator_in_progress", int(agregator_in_progress)
    if agregator_step != mqtt_messages["agregator_step"]:
        mqtt_messages["agregator_step"] = agregator_step
        return "agregator_step", agregator_step
    return None, None


def set_mqtt(topic, message):
    if topic == "agregator_toggle":
        check_for_agregator_toggle()


def loop():
    rpi_peripherals.loop()
    check_for_agregator_progress()


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
