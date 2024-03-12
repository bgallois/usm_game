import asyncio
from bleak import BleakClient
import threading
from pycycling.cycling_power_service import CyclingPowerService

power = -1


def get_power():
    global power
    return power


def start_background_loop(address):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run(address))


async def run(address):
    async with BleakClient(address) as client:
        def my_measurement_handler(data):
            global power
            power = data.instantaneous_power

        await client.is_connected()
        trainer = CyclingPowerService(client)
        trainer.set_cycling_power_measurement_handler(my_measurement_handler)
        await trainer.enable_cycling_power_measurement_notifications()
        await asyncio.sleep(300)
        await trainer.disable_cycling_power_measurement_notifications()


def main(address):
    t = threading.Thread(
        target=start_background_loop, args=(
            address,), daemon=True)
    t.start()
