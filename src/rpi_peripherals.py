import threading
from periphery import GPIO, I2C
import ina219
import log
import time

logger = log.get()

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

BUTTON_LED = 12
BUTTON_IN = 16
RELAY_0 = 18
RELAY_1 = 23
RELAY_2 = 24
RELAY_3 = 25
SHUNT_OHMS = 0.1

button_led = None
button_in = None
relays = []
i2c = None
ina = None
on_relay_pressed = None
on_led_changed = None
button_state = None
on_button_pressed = None


# i2cdetect -y 1


def set_button_led(state):
    button_led.write(bool(state))
    if on_led_changed:
        on_relay_pressed(state)


def get_button_state():
    return int(button_in.read())


def set_relay(num, state):
    relays[num].write(bool(state))
    if on_relay_pressed:
        on_relay_pressed(num, state)


def get_measure():
    voltage = ina.voltage()
    current = ina.current()
    power = ina.power()
    print("Bus Voltage: %.3f V" % voltage)
    print("Current: %.3f mA" % current)
    print("Power: %.3f mW" % power)
    return (voltage, current, power)


def register_on_relay_pressed(func):
    global on_relay_pressed
    on_relay_pressed = func


def register_on_led_changed(func):
    global on_led_changed
    on_led_changed = func


def register_on_button_pressed(func):
    global on_button_pressed
    on_button_pressed = func


def loop():
    global button_state
    logger.info("[RPILOOP]: init begin")
    logger.info("[RPILOOP]: init end")
    while True:
        state = get_button_state()
        if state != button_state:
            button_state = state
            logger.info("[RPILOOP]: button state changed %s" % (state))
            if on_button_pressed:
                on_button_pressed(state)
        time.sleep(0.1)


def init():
    global button_led, button_in, relays, i2c, ina
    button_led = GPIO("/dev/gpiochip0", BUTTON_LED, "out")
    set_button_led(False)
    button_in = GPIO("/dev/gpiochip0", BUTTON_IN, "in", bias="pull_up", inverted=True)
    relays.append(GPIO("/dev/gpiochip0", RELAY_0, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_1, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_2, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_3, "out"))
    for i in range(len(relays)):
        set_relay(i, False)
    i2c = I2C("/dev/i2c-1")
    ina = ina219.INA219(SHUNT_OHMS, i2c)
    ina.configure()
    x = threading.Thread(target=loop)
    x.start()


if __name__ == "__main__":
    init()
    # gpio_in.close()
    # gpio_out.close()