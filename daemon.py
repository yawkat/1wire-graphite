#!/usr/bin/env python3
import re
import time
import traceback

import graphitesend
import os
from typing import Optional

hexpair_regex = r"(?:[0-9a-f]{2} )+[0-9a-f]{2}"


def parse_sensor_data(file_name: str) -> Optional[float]:
    with open(file_name, "r") as f:
        lines = f.read().splitlines()
    if len(lines) != 2:
        raise Exception("Invalid length: %s" % (lines,))
    if not re.fullmatch(hexpair_regex + r" : crc=[0-9a-f]{2} YES", lines[0]):
        raise Exception("First line invalid: %s" % (lines,))
    temp_str = re.fullmatch(hexpair_regex + r" t=(-?\d+)", lines[1]).group(1)
    temp = int(temp_str) / 1000.0
    # todo: negative values
    if temp > 80:
        return
    return temp


graphitesend.init(graphite_server="192.168.1.3", prefix="1wire")

sensor_dir = "sensors"

print("Beginning read loop.")

while True:
    collected_data = {}
    for f in os.listdir(sensor_dir):
        # noinspection PyBroadException
        try:
            collected_data[f] = parse_sensor_data(os.path.join(sensor_dir, f))
        except:
            traceback.print_exc()
    if len(collected_data) > 0:
        graphitesend.send_dict(collected_data)
    else:
        print("No data collected")
    time.sleep(20)
