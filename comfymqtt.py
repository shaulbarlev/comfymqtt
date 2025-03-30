#! /usr/bin/env python3
from evdev import InputDevice, categorize,ecodes, list_devices
import paho.mqtt.client as mqtt
from config import MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE
from keymap import KEY_MAP


client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
client.publish("comfy/test", "hello from python!")


devices = [InputDevice(path) for path in list_devices()]
for device in devices:
    print(device.path, device.name)
    
keyboard = InputDevice('/dev/input/event2')

for event in keyboard.read_loop():
    if event.type == ecodes.EV_KEY:
        key_event = categorize(event)
        if key_event.keystate == 1:
            print(key_event.keycode, key_event.keystate)
            key_name = key_event.keycode.replace("KEY_", "")
            if key_name in KEY_MAP:
                print(f"Key: {key_name} => {KEY_MAP[key_name]}")