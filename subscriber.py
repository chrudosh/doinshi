# Import required libraries
import mqtt
from machine import Pin
from time import sleep
import network
from mqtt import MQTTClient
import dht
import json
from lcd import Lcd_i2c
import neopixel

# ========================
# CONFIGURATION CONSTANTS
# ========================
MQTT_TOPIC = 'stranma21/dht11'  # Topic to subscribe to (matches publisher)
wifi_ssid = 'MQTT3IT'
wifi_password = 'vyuka3ITmqtt'
mqtt_server = b'mqtt.local'
mqtt_username = b''
mqtt_password = b''

# ========================
# MQTT CONNECTION SETTINGS
# ========================
MQTT_SERVER = mqtt_server
MQTT_PORT = 1883
MQTT_USER = mqtt_username
MQTT_PASSWORD = mqtt_password
MQTT_CLIENT_ID = b"display"  # Unique MQTT client identifier
MQTT_KEEPALIVE = 7200

# ========================
# HARDWARE SETUP
# ========================
stop_button = Pin(20, pull=Pin.PULL_UP)     # Stop button connected to GPIO 20
d = dht.DHT11(Pin(3))                       # (Not used here, but included)

# Setup LCD display via I2C
i2c = machine.I2C(sda=machine.Pin(0), scl=machine.Pin(1))
lcd = Lcd_i2c(i2c)

# Setup a NeoPixel LED for status indication
led = neopixel.NeoPixel(machine.Pin(28), 1)


def initialize_wifi(ssid, password):
    """Connect to Wi-Fi and update LED to indicate status."""
    led[0] = (0, 0, 255)  # Blue = connecting
    led.write()

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait up to 10 seconds for a connection
    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        sleep(1)

    # Check connection result
    if wlan.status() != 3:
        return False
    else:
        print('Connection successful!')
        print('IP address:', wlan.ifconfig()[0])
        return True


def connect_mqtt():
    """Connect to the MQTT broker and return a client instance."""
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


def update(topic, payload):
    """Callback function triggered when new MQTT data is received."""
    led[0] = (0, 255, 0)  # Green = receiving data
    led.write()

    # Decode JSON payload from bytes to dictionary
    data = json.loads(payload.decode())

    # Display readings on LCD
    lcd.clear()
    lcd.write(f"temperature: {data['temperature']}{data['temperature_units']}")
    lcd.set_cursor(0, 1)
    lcd.write(f"humidity: {data['humidity']}{data['humidity_units']}")

    led[0] = (0, 0, 0)  # Turn LED off after displaying
    led.write()


# ========================
# MAIN PROGRAM LOOP
# ========================
try:
    if not initialize_wifi(wifi_ssid, wifi_password):
        print('Error connecting to the network... exiting program')
        led[0] = (255, 0, 0)  # Red = connection failed
        led.write()
    else:
        # Connect to MQTT broker and subscribe to topic
        client = connect_mqtt()
        client.set_callback(update)
        client.subscribe(MQTT_TOPIC)

        led[0] = (0, 0, 0)  # Turn LED off (ready state)
        led.write()

        # Wait for messages until the stop button is pressed
        while stop_button.value():
            client.wait_msg()  # Blocks until a message is received
            pass

        # Yellow = program stopped
        led[0] = (255, 255, 0)
        led.write()

except Exception as e:
    print('Error:', e)
    led[0] = (255, 0, 0)  # Red = error
    led.write()
