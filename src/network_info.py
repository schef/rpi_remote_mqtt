#!/usr/bin/env python3

from common import run_bash_cmd


def get_ip_from_usb():
    cmd = "ip addr show usb0"
    lines = run_bash_cmd(cmd)
    for line in lines:
        if "inet" in line:
            try:
                return line.strip().split(" ")[1].split("/")[0]
            except:
                print("Error parsing IP address")
                pass
    return None


def get_ip_from_wifi():
    cmd = "ip addr show wlan0"
    lines = run_bash_cmd(cmd)
    for line in lines:
        if "inet" in line:
            try:
                return line.strip().split(" ")[1].split("/")[0]
            except:
                print("Error parsing IP address")
                pass
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


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
