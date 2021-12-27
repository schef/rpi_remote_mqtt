#!/usr/bin/env python3
import os, sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from common.common import run_bash_cmd


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


def isgoodipv4(s):
    pieces = s.split('.')
    if len(pieces) != 4:
        return False
    try:
        return all(0 <= int(p) < 256 for p in pieces)
    except ValueError:
        return False


def get_public_ip():
    cmd = "dig +short myip.opendns.com @resolver1.opendns.com"
    lines = run_bash_cmd(cmd)
    if len(lines) == 1 and isgoodipv4(lines[0]):
        return lines[0]
    return None


if __name__ == "__main__":
    import readline
    import rlcompleter
    import code

    readline.parse_and_bind("tab: complete")
    code.interact(local=locals())
