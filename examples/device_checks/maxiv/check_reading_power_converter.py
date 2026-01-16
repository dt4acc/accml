import asyncio

import tango

from accml.custom.tango.devices.power_converter import PowerConverter

print(tango.__version__)


async def run_device():
    pc = PowerConverter(
        name="pc",
        trl="r1-d100101cab16/mag/psdh-01",
        setpoint_name="current_set",
        readback_name="current_readback",
    )
    t = await pc.connect()
    t
    await pc.stage()
    d = await pc.describe()
    r = await pc.read()
    print(r)
    await pc.unstage()


def main():
    # need some catalog so that I can read back the data
    cat = catalog["heavy_local"]
    pc = PowerConverter(
        name="pc",
        trl="SimpleTangoServer/test/power_converter_Q3P2T6R",
        setpoint_name="current_setpoint",
        readback_name="current_readback",
    )

    async def connect():
        await pc.connect()

    # Seems that connect needs to demanded explicitly
    asyncio.run(connect())

    RE = RunEngine()
    RE.subscribe(cat.v1.insert)
    (uid,) = RE(bpp.count([pc], 3))
    run = cat[uid]
    print(run.primary.read())
    (uid,) = RE(bpp.list_scan([pc], pc.delta_set_current, [0, 1, -1, 0]))
    run = cat[uid]
    print(run.primary.read())


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()
    pass
