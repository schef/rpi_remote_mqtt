#!/usr/bin/env python3

import json
from common import run_bash_cmd


def get_network_devices():
    cmd = "lshw -class network -json"
    lines = run_bash_cmd(cmd)
    if "WARNING" in lines[0]: lines.pop(0)
    if "WARNING" in lines[-1]: lines.pop(-1)
    return json.loads("".join(lines))


def filter_network_devices(devices, productType):
    result = []
    for device in devices:

        if ('description' in device and productType in device['description'].lower()) or ('product' in device and productType in device['product'].lower()):
            result.append(device)
    return result


def get_ethernet_devices(devices):
    return filter_network_devices(devices, "ethernet")


def get_wireless_devices(devices):
    return filter_network_devices(devices, "wireless")


def get_mac_from_device(device):
    return device["serial"]


def get_ip_from_device(device):
    if "configuration" in device:
        if "ip" in device["configuration"]:
            return device["configuration"]["ip"]
    return None


def get_ip_from_vpn():
    cmd = "ip addr show tun0"
    lines = run_bash_cmd(cmd)
    for line in lines:
        if "inet" in line:
            try:
                return line.strip().split(" ")[1].split("/")[0]
            except:
                print("Error parsing IP address")
                pass
    return None


def get_network_traffic():
    cmd = "vnstat --json t"
    lines = run_bash_cmd(cmd)
    return "\n".join(lines)


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
