import re
from common import run_bash_cmd


# N11
# soc_dts0  43.0°C
# soc_dts1  45.0°C

# raspberry
# cpu-thermal  55.0°C

# tuxedo
# acpitz        48.0°C
# pch_skylake   43.0°C
# iwlwifi_1     40.0°C
# x86_pkg_temp  48.0°C

def clean_string(string):
    string = re.sub(' +', ' ', string)
    string = re.sub('\t+', ' ', string)
    string = string.strip()
    return string


def get_temperature():
    temperature = -1000.0
    try:
        sensors_lines = run_bash_cmd("paste <(cat /sys/class/thermal/thermal_zone*/type) <(cat /sys/class/thermal/thermal_zone*/temp)")
        for line in sensors_lines:
            clean_line = clean_string(line)
            fields = clean_line.split(" ")
            temp = int(fields[1]) / 1000
            if temp > temperature:
                temperature = temp
        if temperature > -1000.0:
            print("get_temperature[%f]" % (temperature))
            return temperature
        else:
            print("ERROR: get_temperature[0.0], not found")
            temperature = 0.0
    except:
        print("ERROR: get_temperature[0.0], can't parse")
        temperature = 0.0
    return temperature


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
