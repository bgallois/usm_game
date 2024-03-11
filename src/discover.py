import asyncio
from bleak import discover


async def run():
    devices = await discover()
    for d in devices:
        print(d)


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())