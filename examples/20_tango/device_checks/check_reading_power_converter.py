import asyncio
import logging


logging.basicConfig(level=logging.WARNING)
from accml.custom.tango.devices.power_converter import PowerConverter

from bluesky import RunEngine
import bluesky.plans as bpp
from databroker import catalog
import bluesky.plan_stubs as bps

import tango

print(tango.__version__)


async def run_device():
    trl = "SimpleTangoServer/test/power_converter_Q3P2T6R"
    trl = "AN01-AR/EM/CQLN.03-pc"
    pc = PowerConverter(
        name="pc",
        trl=trl,
        # setpoint_name="current_setpoint",
        # readback_name="current_readback",
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
    trl = "SimpleTangoServer/test/power_converter_Q3P2T6R"
    trl = "AN01-AR/EM/CQLN.03-pc"
    cat = catalog["heavy_local"]
    pc = PowerConverter(
        name="pc",
        trl=trl,
        # setpoint_name="current_setpoint",
        # readback_name="current_readback",
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

    def per_step(detectors, motor, step):
        yield from bps.mv(motor, step)
        yield from bps.sleep(2.0)
        yield from bps.trigger_and_read(detectors + [motor])

    (uid,) = RE(bpp.list_scan([pc], pc.current_set, [0, 1, -1, 0], per_step=per_step))
    run = cat[uid]
    print(run.primary.read())


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()
    pass
