import gpiozero
from gpiozero.pins.mock import MockFactory
gpiozero.Device.pin_factory = MockFactory()

led = None

def set_led(state):
    if state:
        led.on()
    else:
        led.off()


if __name__ == "__main__":
    led = gpiozero.LED(26)
