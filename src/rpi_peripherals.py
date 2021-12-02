from gpiozero import LED

led = None

def set_led(state):
    if state:
        led.on()
    else:
        led.off()


if __name__ == "__main__":
    led = LED(26)
