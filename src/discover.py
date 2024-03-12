import asyncio
from bleak import BleakScanner


async def main():
    return await BleakScanner.discover()


def get_devices():
    return asyncio.run(main())
