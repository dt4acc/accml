import asyncio
import pprint

from accml.custom.tango.devices.tunes import Tunes

import tango
print(tango.__version__)

async def run_device():
    trl = "SimpleTangoServer/test/tune_device"
    trl = "PHYSICS/SOLEIL/TUNE"
    trl = "simulator/ringsimulator/ringsimulator"
    tune = Tunes(name="tunes", trl=trl)
    await tune.connect()
    await tune.stage()
    d = await tune.describe()
    # Useful to understand the precision certain parameters are
    # shown with
    print("tune description")
    pprint.pprint(d)

    r1 = await tune.read()
    r = await tune.read()
    print("tune read")
    pprint.pprint(r)
    lh = "tunes-Tune_h"
    lv = "tunes-Tune_v"
    dt_x = r[lh]["timestamp"] - r1[lh]["timestamp"]
    dt_y = r[lv]["timestamp"] - r1[lv]["timestamp"]
    dT_x = r[lh]["value"] - r1[lh]["value"]
    dT_y = r[lv]["value"] - r1[lv]["value"]
    pprint.pprint(f"tune  time reading  r1 -> r  {dt_x=}, {dt_y=}")
    pprint.pprint(f"tune change r1 -> r  {dT_x=}, {dT_y=}")
    await tune.unstage()

def main():
    pass


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()
