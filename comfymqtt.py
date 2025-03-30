#! /usr/bin/env python3
from evdev import InputDevice, categorize,ecodes, list_devices
import paho.mqtt.client as mqtt
from config import MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE
from keymap import KEY_MAP
import json
import time
import sys
import threading

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker at {MQTT_BROKER}")
    else:
        print(f"Failed to connect to MQTT broker with result code {rc}")
        sys.exit(1)

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")

# Setup MQTT client with callbacks
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_publish = on_publish

try:
    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    client.loop_start()  # Start the network loop in a separate thread
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    sys.exit(1)

# Give the connection a moment to establish
time.sleep(1)

def discovery_message(sensor_id):
    discovery_topic = f"homeassistant/sensor/comfy/{sensor_id}/config"
    payload = {
        "name": f"{sensor_id}",
        "state_topic": f"comfy/sensor/{sensor_id}",
        "unique_id": f"comfy_{sensor_id}_sensor",
        "device_class": "none",
        "device": {
            "identifiers": ["comfy"],
            "name": "Comfy",
            "manufacturer": "Orange Pi"
        }
    }
    return discovery_topic, payload

# Function to set key back to idle after delay
def reset_key_state(sensor_name, delay=0.5):
    time.sleep(delay)
    state_topic = f"comfy/sensor/{sensor_name}"
    client.publish(state_topic, "idle", qos=1)
    print(f"Reset {sensor_name} to idle")

# Send discovery messages
print("Sending discovery messages...")
for key_name in KEY_MAP:
    topic, payload = discovery_message(key_name)
    result = client.publish(topic, json.dumps(payload), qos=1, retain=True)
    print(f"Publishing to {topic}: {result.rc}")
    time.sleep(0.1)  # Small delay between messages to avoid flooding

print("Discovery messages sent. Waiting a moment for messages to be processed...")
time.sleep(2)  # Give Home Assistant time to process messages

# Find input devices
devices = [InputDevice(path) for path in list_devices()]
for device in devices:
    print(device.path, device.name)
    
try:
    keyboard = InputDevice('/dev/input/by-id/usb-_COMFY-5_USB_Keyboard-event-kbd')
    print(f"Using keyboard: {keyboard.name}")
except Exception as e:
    print(f"Error opening keyboard: {e}")
    client.loop_stop()
    sys.exit(1)

print("Listening for key events. Press Ctrl+C to exit.")
try:
    for event in keyboard.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keystate == 1:  # Key pressed
                print(key_event.keycode, key_event.keystate)
                key_name = key_event.keycode.replace("KEY_", "")
                if key_name in KEY_MAP:
                    sensor_name = KEY_MAP[key_name]
                    print(f"Key: {key_name} => {sensor_name}")
                    # Publish the pressed state
                    state_topic = f"comfy/sensor/{sensor_name}"
                    client.publish(state_topic, "pressed", qos=1)
                    # Start a timer to set it back to idle after 0.5 seconds
                    timer_thread = threading.Thread(target=reset_key_state, args=(sensor_name,))
                    timer_thread.daemon = True  # Thread will exit when main program exits
                    timer_thread.start()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.loop_stop()
    client.disconnect()