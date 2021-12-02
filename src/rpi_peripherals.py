from periphery import GPIO

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

BUTTON_LED = 12
BUTTON_IN = 16
RELAY_1 = 18
RELAY_2 = 23
RELAY_3 = 24
RELAY_4 = 25

button_led = None
button_in = None
relays = []


def set_button_led(state):
    button_led.write(state)


def get_button_state():
    return button_in.read()

def set_relay(num, state):
    relays[num].write(state)

if __name__ == "__main__":
    button_led = GPIO("/dev/gpiochip0", BUTTON_LED, "out")
    button_in = GPIO("/dev/gpiochip0", BUTTON_IN, "in", bias="pull_up")
    relays.append(GPIO("/dev/gpiochip0", RELAY_1, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_2, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_3, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_4, "out"))

    # gpio_in.close()
    # gpio_out.close()
