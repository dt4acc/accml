import asyncio
import pprint

from accml.custom.tango.devices.tunes import Tunes


async def run_device():
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
    dT_x = r["tunes-Tune_h"]["timestamp"] - r1["tunes-Tune_h"]["timestamp"]
    dT_y = r["tunes-Tune_v"]["timestamp"] - r1["tunes-Tune_v"]["timestamp"]
    pprint.pprint(f"tune change r1 -> r x {dT_x}, {dT_y}")
    await tune.unstage()

def main():
    pass


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()
