import asyncio
import logging

from typing import Annotated as A

logging.basicConfig(level=logging.WARNING)

from ophyd_async.tango.core import  tango_signal_r, tango_signal_rw
from bluesky import RunEngine
import bluesky.plans as bpp
from databroker import catalog
from ophyd_async.tango.core import TangoReadable

from ophyd_async.core import SignalR, SignalRW
from ophyd_async.core import StandardReadableFormat as Format
from ophyd_async.tango.core import TangoPolling


class Powerconverter(TangoReadable):
    current_setpoint: A[SignalRW[float], Format.HINTED_SIGNAL, TangoPolling(1.0, 0.1, 0.1)]
    current_readback: A[SignalR[float], TangoPolling(0.1, 0.1, 0.1)]


async def run_device():
    pc = Powerconverter(
        name="pc",
        trl="SimpleTangoServer/test/power_converter_Q3P2T6R",
    )
    await pc.connect()
    await pc.stage()
    r = await pc.read()
    print(r)
    await pc.unstage()



def main():

    cat = catalog["heavy_local"]
    pc = Powerconverter(
        name="pc",
        trl="SimpleTangoServer/test/power_converter_Q3P2T6R",
    )

    async def connect():
        await pc.connect()

    # Seems that connect needs to demanded explicitly
    asyncio.run(connect())

    RE = RunEngine()
    RE.subscribe(cat.v1.insert)
    uid, = RE(bpp.count([pc], 3))
    run = cat[uid]
    print(run.primary.read())


if __name__ == "__main__":
    # you can only run one at once
    asyncio.run(run_device())
    # main()