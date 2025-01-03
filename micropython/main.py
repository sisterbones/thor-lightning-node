
import ubinascii
import json
import machine
import time
from random import randint
from machine import Pin, UART

from umqtt.robust import MQTTClient

import config

if not config.get("MQTT_IP"):
    config.init()
    
uart = UART(2, 115200, rx=Pin(44), timeout=1000)
uart.init(115200, bits=8, parity=None, stop=1)

c = MQTTClient(ubinascii.hexlify(machine.unique_id()), config.get("MQTT_IP"))
if config.get("MQTT_USERNAME"):
    c.user = config.get("MQTT_USERNAME")
if config.get("MQTT_PASSWORD"):
    c.pswd = config.get("MQTT_PASSWORD")
    
TESTING = 0

if TESTING:
    print("TESTING IS ACTIVE")
    while True:
        data = "~NOISY"
        data = data[1:]
        if data == "NOISY":
            message = {
                    "type": "lightning", "error": "noisy", "timestamp": time.time()
                }
        else:
            data = data.split(";");
            message = {"type": "lighting", "distance": int(data[1].split(":")[1]), "timestamp":time.time()}
        
        try:
            c.connect()
            c.publish(b'thor/update/lightning', json.dumps(message).encode('UTF-8'))
            print("Sending {}".format(message))
            c.disconnect()
        except Exception as e:
            if e == 5:
                print("!!! Unauthorised. [MQTT]")
            else:
                print("!!! {} [MQTT]".format(e))
            config.init()
            if config.get("MQTT_USERNAME"):
                c.user = config.get("MQTT_USERNAME")
            if config.get("MQTT_PASSWORD"):
                c.pswd = config.get("MQTT_PASSWORD")
                
        time.sleep(30)

while True:
    uart.flush()
    data = uart.readline()
    
    if data is None:
        continue
    
    try:
        data = data.decode('utf-8')
        print("RECEIVED: {}".format(data))
    except UnicodeError:
        print("RECEIVED: {}".format(data))
        continue
    
    if not data.startswith("~"):
        continue
    
    data = data[1:]
    if data == "NOISY":
        message = {
                "type": "lightning", "error": "noisy", "timestamp": time.time()
            }
    else:
        data = data.split(";");
        message = {"type": "lighting", "distance": int(data[1].split(":")[1]), "timestamp":time.time()}
    
    try:
        c.connect()
        c.publish(b'thor/update/lightning', json.dumps(message).encode('UTF-8'))
        print("Sending {}".format(message))
        c.disconnect()
    except Exception as e:
        if e == 5:
            print("!!! Unauthorised. [MQTT]")
        else:
            print("!!! {} [MQTT]".format(e))
        config.init()
        if config.get("MQTT_USERNAME"):
            c.user = config.get("MQTT_USERNAME")
        if config.get("MQTT_PASSWORD"):
            c.pswd = config.get("MQTT_PASSWORD")
