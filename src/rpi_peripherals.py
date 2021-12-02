from periphery import GPIO, I2C
import ina219

# https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf

BUTTON_LED = 12
BUTTON_IN = 16
RELAY_1 = 18
RELAY_2 = 23
RELAY_3 = 24
RELAY_4 = 25
SHUNT_OHMS = 0.1

button_led = None
button_in = None
relays = []
i2c = None
ina = None

# i2cdetect -y 1


def set_button_led(state):
    button_led.write(bool(state))


def get_button_state():
    return int(button_in.read())


def set_relay(num, state):
    relays[num].write(bool(state))


def get_measure():
    voltage = ina.voltage()
    current = ina.current()
    power = ina.power()
    print("Bus Voltage: %.3f V" % voltage)
    print("Current: %.3f mA" % current)
    print("Power: %.3f mW" % power)
    return (voltage, current, power)


if __name__ == "__main__":
    button_led = GPIO("/dev/gpiochip0", BUTTON_LED, "out")
    set_button_led(False)
    button_in = GPIO("/dev/gpiochip0", BUTTON_IN, "in", bias="pull_up", inverted=True)
    relays.append(GPIO("/dev/gpiochip0", RELAY_1, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_2, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_3, "out"))
    relays.append(GPIO("/dev/gpiochip0", RELAY_4, "out"))
    for i in range(len(relays)):
        set_relay(i, False)
    i2c = I2C("/dev/i2c-1")
    ina = ina219.INA219(SHUNT_OHMS, i2c)
    ina.configure()


    # gpio_in.close()
    # gpio_out.close()
