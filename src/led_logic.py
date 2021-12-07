import rpi_peripherals
import common
import time
import log

logger = log.get()

blink_frames = 1
inverted_light = False

led_start_timestamp = 0
led_timeout = 5000

led_blink_frame = 100
led_total_frame = 1000


def set_led(frames, inverted):
    global blink_frames, inverted_light, led_start_timestamp
    blink_frames = frames
    inverted_light = inverted
    if frames == 0:
        led_start_timestamp = 0
    else:
        led_start_timestamp = common.get_millis()


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
    time = common.millis_passed(led_start_timestamp)
    logger.info("[LED]: time %d" % (time))
    for frame in range(get_number_of_frames() + 1):
        if is_time_in_timeframe(time, frame):
            logger.info("[LED]: is_time_in_timeframe %d, %d" % (time, frame))
            if not rpi_peripherals.get_button_led_state() and is_time_in_timeframe_for_blink(time, frame):
                logger.info("[LED]: time for blink")
                if inverted_light:
                    rpi_peripherals.set_button_led(True)
                else:
                    rpi_peripherals.set_button_led(False)
            if rpi_peripherals.get_button_led_state() and not is_time_in_timeframe_for_blink(time, frame):
                logger.info("[LED]: time for off")
                if (inverted_light):
                    rpi_peripherals.set_button_led(True)
                else:
                    rpi_peripherals.set_button_led(False)
    time.sleep(0.5)


def init_test():
    rpi_peripherals.init()


def loop_test():
    while True:
        loop()


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
