from periphery import GPIO

led = None


def set_led(state):
    led.write(state)


if __name__ == "__main__":
    # Open GPIO /dev/gpiochip0 line 10 with input direction
    # gpio_in = GPIO("/dev/gpiochip0", 10, "in")
    # Open GPIO /dev/gpiochip0 line 12 with output direction
    led = GPIO("/dev/gpiochip0", 26, "out")

    # value = gpio_in.read()

    # gpio_in.close()
    # gpio_out.close()
