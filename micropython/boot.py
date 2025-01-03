
import machine
import network
import time

import config
from logging import Logger

log = Logger()

red = machine.Pin(46, machine.Pin.OUT)
green = machine.Pin(0, machine.Pin.OUT)

WIFI_NETWORK=config.get("WIFI_SSID")
WIFI_PASSWORD=config.get("WIFI_PASSWORD")

NO_WIFI_CONFIGURED = 0

if not WIFI_NETWORK:
    NO_WIFI_CONFIGURED = 1
    red.value(1)
else:
    green.value(1)
    
log.debug(NO_WIFI_CONFIGURED)
    
if NO_WIFI_CONFIGURED:
    try:
        with open("wifi.txt", "r") as ff:
            wifi = ff.read()
        wifi_options_list = wifi.split("\n")
        wifi_options = {}
        for option in wifi_options_list:
            option = option.split("=", 1)
            wifi_options[option[0]] = option[1]
        WIFI_NETWORK = wifi_options.get("SSID", None)
        WIFI_PASSWORD = wifi_options.get("PASSWORD", None)
    except:
        log.critical("Couldn't connect to Wi-Fi.")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
try:
    wlan.connect(WIFI_NETWORK, WIFI_PASSWORD)
except OSError as e:
    log.critical("Couldn't connect to Wi-Fi. Error code: {}".format(e))
    log.critical("SSID: {}, PASSWORD: {}".format(WIFI_NETWORK, WIFI_PASSWORD))
    
config.set("WIFI_SSID", WIFI_NETWORK)
config.set("WIFI_PASSWORD", WIFI_PASSWORD)

if config.init_error:
    config.init()
