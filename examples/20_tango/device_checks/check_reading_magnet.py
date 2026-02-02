import asyncio
import pprint

from accml.custom.tango.devices.magnet import Magnet

async def run_device():
    trl = "AN01-AR/EM-QP/QD02.02"
    quad = Magnet(name="quads", trl=trl)
    await quad.connect()
    await quad.stage()
    d = await quad.describe()
    # Useful to understand the precision certain parameters are
    # shown with
    print("quad description")
    pprint.pprint(d)
    print("Read 1")
    pprint.pp(await quad.read())
    await quad.Strength.set(0.1)  # awaited write already done
    print("Read 2")
    pprint.pp(await quad.read())
    await quad.set(0.2)
    print("Read 3")
    pprint.pp(await quad.read())
    await quad.set(0.0)
    print("Read 4")
    pprint.pp(await quad.read())
    await quad.unstage()

def main():
    pass


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()
