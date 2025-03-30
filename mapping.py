#! /usr/bin/env python3

key_map = {
    "W": "earpiece_down",
    "A": "earpiece_up"
}

key_name = "A"
sensor_id = key_map.get(key_name, "unknown")
print(sensor_id)  # "earpiece_down"