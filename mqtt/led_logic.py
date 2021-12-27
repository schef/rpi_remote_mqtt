import os, sys

import credentials
import rpi_peripherals_ekofarma as rpi_peripherals

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common import log, common

logger = log.get()

blink_frames = 0
inverted_light = False

led_start_timestamp = 0
led_timeout = 5000

led_blink_frame = 200
led_total_frame = 1000


def set_led(frames, inverted=False):
    logger.info("[LED]: set_led %d %s" % (frames, inverted))
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
    # logger.info("time %d" % (time))
    should_be_on = False
    for frame in range(1, get_number_of_frames() + 1):
        if blink_frames >= frame:
            if is_time_in_timeframe_for_blink(time, frame):
                # logger.info("should be on")
                should_be_on = True

    if should_be_on:
        if not inverted_light:
            if not rpi_peripherals.get_button_led_state():
                rpi_peripherals.set_button_led(True)
        else:
            if rpi_peripherals.get_button_led_state():
                rpi_peripherals.set_button_led(False)
    else:
        if not inverted_light:
            if rpi_peripherals.get_button_led_state():
                rpi_peripherals.set_button_led(False)
        else:
            if not rpi_peripherals.get_button_led_state():
                rpi_peripherals.set_button_led(True)


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
