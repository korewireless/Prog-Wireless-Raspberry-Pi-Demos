##############################################
# Twilio MQTT Demo for Programmable Wireless #
##############################################
from time import sleep
from sys import exit
from smbus import SMBus
import json
import paho.mqtt.client as mqtt

##############################################
# Global variables                           #
##############################################
# EDIT THESE
MQTT_CLIENT_ID = "SOME_RANDOM_STRING"
MQTT_PUBLISH_TOPIC = "SOME_RANDOM_STRING/info"
MQTT_ADDRESS = "broker.hivemq.com"
MQTT_BROKER_PORT = 1883
MQTT_USERNAME = "YOUR_USERNAME"
MQTT_PASSWORD = "YOUR_PASSWORD"

##############################################
# MCP9808 driver                             #
##############################################
MCP9808_I2CADDR_DEFAULT = 0x18
MCP9808_REG_CONFIG = 0x01
MCP9808_REG_AMBIENT_TEMP = 0x05
MCP9808_REG_MANUF_ID = 0x06
MCP9808_REG_DEVICE_ID = 0x07

class MCP9808(object):
    def __init__(self, address=MCP9808_I2CADDR_DEFAULT, bus=None):
        self.address = address
        if bus: self.bus = SMBus(bus)

    def check(self):
        # Check we can read correct Manufacturer ID and Device ID values
        try:
            mid_data = self.bus.read_i2c_block_data(self.address, MCP9808_REG_MANUF_ID, 2)
            did_data = self.bus.read_i2c_block_data(self.address, MCP9808_REG_DEVICE_ID, 2)
            mid_value = (mid_data[0] << 8) | mid_data[1]
            did_value = (did_data[0] << 8) | did_data[1]
            return (mid_value == 0x0054 and did_value == 0x0400)
        except:
            return False

    def read(self):
        # Get the ambient temperature
        temp_data = self.bus.read_i2c_block_data(self.address, MCP9808_REG_AMBIENT_TEMP, 2)

        # Scale and convert to signed Celsius value.
        temp_raw = (temp_data[0] << 8) | temp_data[1]
        temp_cel = (temp_raw & 0x0FFF) / 16.0
        if temp_raw & 0x1000: temp_cel -= 256.0
        return temp_cel

##############################################
# The main application code                  #
##############################################
def app_loop():
    tx_count = 1
    try:
        # Setup the temperature sensor
        sensor = MCP9808(bus=1)
        sensor_state = sensor.check()
        if sensor_state is False:
            print("[ERROR] No MCP9808 attached")
            exit(1)

        #  Main application loop
        while True:
            temp = sensor.read()
            print("{}. Ambient temperature is {:.02f} celsius".format(tx_count, temp))
            tx_count +=1

            # Craft a message to the cloud
            msg_formatted = json.dumps({
                'device_id': MQTT_CLIENT_ID + "-device",
                'temperature': temp,
                'units': 'celsius',
                'shenanigans': "none"
            })

            # Publish the message by MQTT
            client.publish(MQTT_PUBLISH_TOPIC, msg_formatted)

            # Loop every minute
            sleep(60)
    except KeyboardInterrupt:
        print(" MQTT Demo 1for Programmable Wireless stopped")
    except OSError:
        print("[ERROR] Cannot read sensor, check connection")

##############################################
# Called from the command line               #
##############################################
if __name__ == '__main__':
    print ("Starting MQTT Demo 1 for Programmable Wireless")

    # Setup MQTT
    client = mqtt.Client("TWILIO DEMO 1")
    client.username_pw_set(MQTT_USERNAME, password=MQTT_PASSWORD)
    client.connect(MQTT_ADDRESS, MQTT_BROKER_PORT, 60)
    client.loop_start()

    # Run the main loop
    app_loop()
