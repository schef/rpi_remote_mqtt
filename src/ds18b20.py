#!/usr/bin/env python

import os
import re
from glob import glob
import time

# Folder with 1-Wire devices
w1DeviceFolder = '/sys/bus/w1/devices'

# Function that returns array with IDs of all found thermometers
def find_thermometers():
    # Get all devices
    w1Devices = glob(w1DeviceFolder + '/*/')
    # Create regular expression to filter only those starting with '28', which is thermometer
    w1ThermometerCode = re.compile(r'28-\d+')
    # Initialize the array
    thermometers = []
    # Go through all devices
    for device in w1Devices:
        # Read the device code
        deviceCode = device[len(w1DeviceFolder) + 1:-1]
        # If the code matches thermometer code add it to the array
        if w1ThermometerCode.match(deviceCode):
            thermometers.append(deviceCode)
    # Return the array
    return thermometers


# Function that reads and returns the raw content of 'w1_slave' file
def read_temp_raw(deviceCode):
    f = open(w1DeviceFolder + '/' + deviceCode + '/w1_slave', 'r')
    lines = f.readlines()
    f.close()
    return lines


# Function that reads the temperature from raw file content
def read_temp(deviceCode):
    # Read the raw temperature data
    lines = read_temp_raw(deviceCode)
    # Wait until the data is valid - end of the first line reads 'YES'
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(deviceCode)
    # Read the temperature, that is on the second line
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        # Convert the temperature number to Celsius
        temp_c = float(temp_string) / 1000.0
        # Convert the temperature to Fahrenheit
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        # Return formatted sensor data
        return {
            'thermometerID': deviceCode,
            'celsius': temp_c,
            'fehrenheit': temp_f
        }


# Function that pretty prints the sensor data
def print_temperature(data):
    print('|________')
    print('|')
    print('| Thermometer {}'.format(data['thermometerID']))
    print('| Celsius:    {}'.format(data['celsius']))
    print('| Fahrenheit: {}'.format(data['fehrenheit']))


# Function that prints actual timestamp
def print_timestamp():
    print(' _________________________')
    print('|')
    print('| Measurement from: ' + time.strftime('%Y-%m-%d %H:%M:%S'))


# Main function
def main():
    # Find all connected thermometers
    thermometers = find_thermometers()
    # Print actual timestamp
    print_timestamp()
    # Go through all connected thermometers
    for thermometer in thermometers:
        # Pretty print sensor data
        print_temperature(read_temp(thermometer))


# Run the main function when the script is executed
if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())