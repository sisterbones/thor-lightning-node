# Ported from the regular Python version.
import binascii
import errno
import json
import logging
import machine
#import uuid
import socket

import mrequests as requests
#from rich.console import Console
#from rich.logging import RichHandler

#FORMAT = "%(message)s"
#logging.basicConfig(
#    level="DEBUG", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(markup=True, rich_tracebacks=True)]
#)
log = logging.Logger()

config = {}

init_error = False

def get(key, fallback=""):
    return config.get(key, fallback)

def set(key, value):
    global config
    config[key] = value
    with open("config.json", "w") as ff:
        json.dump(config, ff)
    return config

# Init
def init():
    # Get MQTT Broker IP address, MQTT server password and username
    # Following kinda stolen from https://github.com/jholtmann/ip_discovery
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)

    server_address = ('255.255.255.255', 51366)
    message = 'thor_node_broadcast;{}'.format(binascii.hexlify(machine.unique_id()))

    try_times = 0

    try:
        log.info('Waiting to connect to THOR server...')
        while True:
            # Send data
            log.debug('sending: ' + message)
            sent = sock.sendto(message.encode(), server_address)

            # Receive response
            log.debug('waiting to receive')
            try:
                data, server = sock.recvfrom(4096)
            except TimeoutError:
                log.critical('We\'re having problems connecting.\nERROR: Timed out')
                continue

            if data.decode('UTF-8').startswith('thor_server_response'):
                decoded = data.decode('UTF-8')
                results = decoded.split(";")
                log.info('Found server to connect to!!')
                log.info('Server ip: ' + str(server[0]))
                hub_ip = str(server[0])

                log.info(
                    'Found THOR server. Waiting for response...\nHub IP: {0}:{1}\nMy IP: {2}'.format(
                        hub_ip, results[2].split(":")[1], results[1].split(":")[1]))
                set("HUB_IP", hub_ip)
                set("HUB_PORT", results[2].split(":")[1])
                set("MY_IP", results[1].split(":")[1])
                break
            else:
                log.error('IP verification failed')
                try_times += 1
                if try_times == 5:
                    log.critical('We\'re having problems connecting.')

            print('Trying again...')
    finally:
        sock.close()

    # Now grab MQTT credentials
    registration = requests.get("http://"+get("HUB_IP")+":"+get("HUB_PORT")+"/api/node/register/"+str(binascii.hexlify(machine.unique_id())))
    log.debug(registration.text)
    data = registration.json()
    set("MQTT_IP", data.get('mqtt').get('host', get("HUB_IP")))
    set("MQTT_PORT", data.get("mqtt").get("port"))
    set("MQTT_USERNAME", data.get("mqtt").get("username"))
    set("MQTT_PASSWORD", data.get("mqtt").get("password"))

# Try load the inital config.
try:
    with open("config.json", "r") as ff:
        content = ff.read()
        config = json.loads(content)
except (OSError, ValueError) as exc:
    if exc.errno == errno.EEXIST:
        open("config.json", "x")
    try:
        init()
    except:
        init_error = True

if ("HUB_IP" not in config) or ("HUB_PORT" not in config):
    try:
        init()
    except:
        init_error = True