import asyncio
import pprint

from accml.custom.tango.devices.tunes import Tunes

async def run_device():
    tune = Tunes(name="tunes", trl="SimpleTangoServer/test/tune_device")
    await tune.connect()
    await tune.stage()
    d = await tune.describe()
    r = await tune.read()
    pprint.pprint(r)
    await tune.unstage()

def main():
    pass


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()
