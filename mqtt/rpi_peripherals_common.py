class GPIOTest:
    def __init__(self, pin):
        self.pin = pin

    def write(self, state):
        print(f"TestRelay[{self.pin}].write {state}")


class Relay:
    def __init__(self, pin: int, invert=False, test=False):
        if test:
            self.relay = GPIOTest(pin)
        else:
            from periphery import GPIO
            self.relay = GPIO("/dev/gpiochip0", pin, "out")
        self.state = None
        self.invert = invert

    def set(self, state):
        if self.invert:
            self.relay.write(not bool(state))
        else:
            self.relay.write(bool(state))
        self.state = state

    def get(self):
        return self.state


class Ds18b20Test:
    def __init__(self, address):
        self.address = address
        self.temp = 23.456

    def set(self, temp):
        print(f"Ds18b20Test::set[{self.address}]({temp})")
        self.temp = temp

    def get(self):
        print(f"Ds18b20Test::get[{self.address}]({self.temp})")
        return self.temp


class TemperatureSensor:
    def __init__(self, address, test=False):
        if test:
            self.device = Ds18b20Test(address)
        else:
            from ds18b20 import Ds18b20
            self.device = Ds18b20(address)

    def get(self):
        try:
            return self.device.get()
        except:
            return 0.0

class PowerMeasurementTest:
    def __init__(self, tty):
        pass

    def read_all(self, scaling=False):
        print("PowerMeasurementTest::read_all")
        return {}


class PowerMeasurement:
    def __init__(self, tty, test=False):
        self.tty = tty
        if test:
            self.meter = PowerMeasurementTest(tty)
        else:
            import sdm_modbus
            self.meter = sdm_modbus.SDM72(device=tty, stopbits=1, parity="N", baud=9600, timeout=1, unit=False)

    def get(self):
        return self.meter.read_all(scaling=True)


class PM5100:
    def __init__(self, tty, test=False):
        self.tty = tty
        if test:
            self.meter = PowerMeasurementTest(tty)
        else:
            import schneider_pm5100
            self.pm5100 = schneider_pm5100.configure("/dev/ttyUSB0", 1, 19200)

    def get(self):
        res = self.pm5100.get_readings(instrument, PM5100_REGISTER_MAP)
        print(res)
        return {}
