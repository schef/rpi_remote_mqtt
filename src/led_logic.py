import rpi_peripherals
import common
import log
from time import sleep

logger = log.get()

blink_frames = 0
inverted_light = False

led_start_timestamp = 0
led_timeout = 5000

led_blink_frame = 100
led_total_frame = 1000


def set_led(frames, inverted=False):
    global blink_frames, inverted_light, led_start_timestamp
    blink_frames = frames
    if frames == 0:
        led_start_timestamp = 0
        inverted_light = False
    else:
        led_start_timestamp = common.get_millis()
        inverted_light = inverted


def get_start_frame(frame):
    return (frame - 1) * led_total_frame


def get_end_frame(frame):
    return (frame) * led_total_frame


def get_blink_start_frame(frame):
    return get_start_frame(frame)


def get_blink_end_frame(frame):
    return get_start_frame(frame) + led_blink_frame


def is_time_in_timeframe(time, frame):
    return time >= get_start_frame(frame) and time < get_end_frame(frame)


def is_time_in_timeframe_for_blink(time, frame):
    return time >= get_blink_start_frame(frame) and time < get_blink_end_frame(frame)


def get_number_of_frames():
    return int(led_timeout / led_total_frame)


def loop():
    time = common.millis_passed(led_start_timestamp) % led_timeout
    logger.debug("[LED]: time %d" % (time))
    for frame in range(get_number_of_frames() + 1):
        if blink_frames >= frame:
            if is_time_in_timeframe(time, frame):
                logger.debug("[LED]: in frame %d" % (frame))
                if is_time_in_timeframe_for_blink(time, frame):
                    logger.debug("[LED]: time for blink")
                    if not rpi_peripherals.get_button_led_state():
                        logger.info("[LED]: turn on")
                        rpi_peripherals.set_button_led(True)
                else:
                    if rpi_peripherals.get_button_led_state():
                        logger.info("[LED]: turn off inside")
                        rpi_peripherals.set_button_led(False)
        else:
            if rpi_peripherals.get_button_led_state():
                logger.info("[LED]: turn off outside")
                rpi_peripherals.set_button_led(False)
    sleep(0.01)


def test_init():
    rpi_peripherals.init()


def test_loop():
    while True:
        loop()


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
