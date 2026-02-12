# Import necessary libraries
import mqtt
from machine import Pin
from time import sleep
import network
from mqtt import MQTTClient
import dht
import json

# ========================
# CONFIGURATION CONSTANTS
# ========================
MQTT_TOPIC = 'stranma21/dht11'  # MQTT topic for publishing DHT11 data
wifi_ssid = 'MQTT3IT'           # Wi-Fi SSID
wifi_password = 'vyuka3ITmqtt'  # Wi-Fi password
mqtt_server = b'mqtt.local'     # MQTT broker address
mqtt_username = b''             # Optional username (not used)
mqtt_password = b''             # Optional password (not used)

# ========================
# MQTT CONNECTION SETTINGS
# ========================
MQTT_SERVER = mqtt_server
MQTT_PORT = 1883
MQTT_USER = mqtt_username
MQTT_PASSWORD = mqtt_password
MQTT_CLIENT_ID = b"raspberrypi_picow"  # Unique MQTT client identifier
MQTT_KEEPALIVE = 7200                  # Keepalive interval in seconds

# ========================
# HARDWARE SETUP
# ========================
stop_button = Pin(4, pull=Pin.PULL_UP)  # Stop button connected to GPIO 4
d = dht.DHT11(Pin(3))                   # DHT11 sensor connected to GPIO 3


def get_sensor_readings():
    """Read temperature and humidity from DHT11 sensor."""
    d.measure()
    return d.temperature(), d.humidity()


def initialize_wifi(ssid, password):
    """Connect to the specified Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for Wi-Fi connection (max 10 seconds)
    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.status() >= 3:  # Status 3 means connected
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        sleep(1)

    if wlan.status() != 3:
        # Failed to connect
        return False
    else:
        # Successfully connected
        print('Connection successful!')
        print('IP address:', wlan.ifconfig()[0])
        return True


def connect_mqtt():
    """Initialize and connect to the MQTT broker."""
    try:
        client = MQTTClient(client_id=MQTT_CLIENT_ID,
                            server=MQTT_SERVER,
                            port=MQTT_PORT,
                            keepalive=MQTT_KEEPALIVE)
        client.connect()
        return client
    except Exception as e:
        print('Error connecting to MQTT:', e)
        raise


# ========================
# MAIN PROGRAM LOOP
# ========================
try:
    if not initialize_wifi(wifi_ssid, wifi_password):
        print('Error connecting to the network... exiting program')
    else:
        # Connect to MQTT broker
        client = connect_mqtt()

        # Publish data repeatedly until the stop button is pressed
        while stop_button.value():
            # Read data from DHT11
            temperature, humidity = get_sensor_readings()

            # Create a JSON-formatted payload
            payload = {
                "humidity": humidity,
                "temperature": temperature,
                "humidity_units": "RH%",
                "temperature_units": "C"
            }

            # Publish data to the MQTT topic
            client.publish(MQTT_TOPIC, json.dumps(payload))
            print(payload)

            # Wait before sending next reading
            sleep(5)

except Exception as e:
    print('Error:', e)
