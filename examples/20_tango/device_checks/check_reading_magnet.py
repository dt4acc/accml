import asyncio
import pprint

from accml.custom.tango.devices.magnet import Magnet


async def run_device():
    trl = "AN01-AR/EM-QP/QD02.02"
    quad = Magnet(name="quad", trl=trl)
    await quad.connect()
    await quad.stage()
    d = await quad.describe()
    # Useful to understand the precision certain parameters are
    # shown with
    print("quad description")
    pprint.pprint(d)

    r1 = await quad.read()
    r = await quad.read()
    print("quad read")
    pprint.pprint(r)
    quad_r1 = r["quad-Strength"]["timestamp"] - r1["quad-Strength"]["timestamp"]
    pprint.pprint(f"quad change r1 -> r x {quad_r1}")
    await quad.unstage()

def main():
    pass


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()
