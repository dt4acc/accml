import asyncio
import pprint

from accml.custom.tango.devices.tunes import Tunes


async def run_device():
    trl = "SimpleTangoServer/test/tune_device"
    trl = "PHYSICS/SOLEIL/TUNE"
    tune = Tunes(name="tunes", trl=trl)
    await tune.connect()
    await tune.stage()
    d = await tune.describe()
    r1 = await tune.read()
    r = await tune.read()
    pprint.pprint(r)
    dT_x = r["tunes-hor"]["timestamp"] - r1["tunes-hor"]["timestamp"]
    dT_y = r["tunes-vert"]["timestamp"] - r1["tunes-vert"]["timestamp"]
    pprint.pprint(f"tune change r1 -> r x {dT_x}, {dT_y}")
    await tune.unstage()

def main():
    pass


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()
