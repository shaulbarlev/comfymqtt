#! /usr/bin/env python3
from evdev import InputDevice, categorize,ecodes, list_devices
import paho.mqtt.client as mqtt
        
key_map = {
    "W": "earpiece_down",
    "A": "earpiece_up",
    "J": "cute_row_1",
    "H": "cute_row_2",
    "G": "cute_row_3",
    "F": "cute_row_4",
    "D": "cute_row_5",
    "E": "direction_up",
    "T": "direction_down",
    "Y": "direction_left",
    "R": "direction_right",
    "U": "direction_center",
    "X": "color_1",
    "C": "color_2",
    "V": "color_3",
    "B": "color_4",
    "N": "color_5",
    "K": "color_6",
    "O": "symbol_sun",
    "L": "symbol_moon",
    "S": "symbol_cloud",
    "Z": "symbol_wheel",
    "I": "symbol_stop"
}

client = mqtt.Client()
client.username_pw_set("homeassistant", "homeassistant")
client.connect("192.168.50.232", 1883, 60)

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
            if key_name in key_map:
                print(f"Key: {key_name} => {key_map[key_name]}")