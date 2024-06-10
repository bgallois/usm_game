# ATROCE CODING Disclaimer:
# This code is for educational/experimental purposes only.
# It's a quick and dirty implementation for accessing Bluetooth devices
# and retrieving power data. Can be used with a bot if no device is available.
# Variables are not thread-safe. Only suitable for simple games.

import asyncio
from bleak import BleakClient
import threading
from pycycling.cycling_power_service import CyclingPowerService
import time
import random
import sys


power = -1
stop_flag = False


def get_power():
    global power
    return power


def stop():
    global stop_flag
    stop_flag = True


def start_background_loop(address):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run(address))


async def run(address):
    async with BleakClient(address) as client:
        def my_measurement_handler(data):
            global power
            power = data.instantaneous_power
            if stop_flag:
                power = 0
                sys.exit()

        await client.is_connected()
        trainer = CyclingPowerService(client)
        trainer.set_cycling_power_measurement_handler(my_measurement_handler)
        await trainer.enable_cycling_power_measurement_notifications()
        await asyncio.sleep(36000)
        await trainer.disable_cycling_power_measurement_notifications()


def main(address=None):
    global stop_flag
    stop_flag = False
    if address:
        current = threading.Thread(
            target=start_background_loop, args=(
                address,), daemon=True)
        current.start()
    else:
        current = threading.Thread(target=Bot().cycle, daemon=True)
        current.start()


TIME = time.time()
PREV = 0


class Bot():

    def cycle(self):
        # Random power generator for dev
        global TIME
        global PREV
        global power
        global stop_flag
        while True:
            if time.time() - TIME > 1.5:
                TIME = time.time()
                PREV = random.gauss(150, 50)
            power = max(0, PREV)
            if stop_flag:
                power = 0
                break
