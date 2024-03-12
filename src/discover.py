import asyncio
from bleak import BleakScanner


async def main():
    return await BleakScanner.discover()


def get_devices():
    try:
        return asyncio.run(main())
    except Exception as e:
        print([(e,)])
