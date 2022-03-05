#!/usr/bin/env python3

import os
import datetime
import unittest
import json
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import credentials

TABLE_XPATH = "/html/body/div/div/div/main/div/form/div/div[3]/div[2]/div/table/tbody"


class Base:
    # Foreground:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    # Formatting
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    # End colored text
    END = '\033[0m'
    NC = '\x1b[0m'  # No Color


def getDriver(headless=False):
    opts = Options()
    opts.headless = True
    if headless == True:
        os.environ['MOZ_HEADLESS'] = '1'
    driver = webdriver.Firefox()
    return driver


def convert_time_string_to_seconds(time_string):
    seconds = 0
    if ", " in time_string:
        dayweek, time_string = time_string.split(", ")
        count, multiplicator = dayweek.split(" ")
        match multiplicator:
            case ("day" | "days"):
                seconds += int(count) * 24 * 60 * 60
            case "week":
                seconds += int(count) * 7 * 24 * 60 * 60
    date_time = datetime.datetime.strptime(time_string, "%H:%M:%S")
    a_timedelta = date_time - datetime.datetime(1900, 1, 1)
    seconds += a_timedelta.total_seconds()
    return seconds


def get_location(ip):
    url = f"http://ipinfo.io/{ip}/json"
    response = urlopen(url)
    return json.load(response)


class TestTime(unittest.TestCase):
    def test_string_to_seconds(self):
        self.assertEqual(convert_time_string_to_seconds("00:00:05"), 5)
        self.assertEqual(convert_time_string_to_seconds("1 day, 00:00:00"), 86400)
        self.assertEqual(convert_time_string_to_seconds("0 days, 00:00:00"), 0)
        self.assertEqual(convert_time_string_to_seconds("1 week, 00:00:00"), 604800)


if __name__ == "__main__":
    driver = getDriver(True)
    driver.get(credentials.website)
    driver.find_element(By.ID, "username").send_keys(credentials.username)
    driver.find_element(By.ID, "password").send_keys(credentials.password)
    driver.find_element(By.ID, "submit-button").click()
    driver.get(credentials.website)
    table_xpath = driver.find_element(By.XPATH, TABLE_XPATH)
    devices_xpath = table_xpath.find_elements(by=By.XPATH, value="./*")
    devices = []
    for d in devices_xpath:
        device = {}
        elements = d.find_elements(by=By.XPATH, value="./*")
        device["name"] = elements[0].text
        device["real_address"] = elements[1].text
        device["vpn_address"] = elements[2].text
        device["bytes"] = elements[3].text
        device["connection"] = elements[4].text
        device["seconds"] = convert_time_string_to_seconds(device["connection"])
        devices.append(device)
    driver.close()
    devices = sorted(devices, key=lambda d: d['seconds'])
    len_connection = max([len(k["connection"]) for k in devices])
    len_real_address = max([len(k["real_address"]) for k in devices])
    len_vpn_address = max([len(k["vpn_address"]) for k in devices])
    for device in devices:
        device["location"] = get_location(device["real_address"].split(":")[0])
    for device in devices:
        string = ""
        string += f"{Base.BOLD}{Base.OKGREEN}{device['vpn_address']:<{len_vpn_address}}{Base.END}"
        string += f" {device['real_address']:<{len_real_address}}"
        string += f" {device['connection']:<{len_connection}}"
        string += f" {device['location']['country']}"
        string += f", {device['location']['region']}"
        string += f", {device['location']['city']}"
        string += f", {device['location']['org']}"
        print(string)
