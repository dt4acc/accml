import asyncio
import logging
import time


logging.basicConfig(level=logging.WARNING)

from ophyd_async.core import StandardReadable, AsyncStatus
from ophyd_async.tango.core import tango_signal_r, tango_signal_rw
from bluesky.protocols import Movable, Stoppable, SyncOrAsync, Stageable
from bluesky import RunEngine
import bluesky.plans as bpp
from databroker import catalog


class Powerconverter(StandardReadable, Stoppable, Stageable):
    """a power converter that allows overriding setpoint and readback suffix"""

    def __init__(
        self,
        prefix: str,
        setpoint_suffix: str = None,
        readback_suffix: str = None,
        name="",
        **kwargs,
    ):
        assert readback_suffix is not None
        assert setpoint_suffix is not None

        with self.add_children_as_readables():
            # Todo: add hints
            # fmt:off
            self.setpoint = tango_signal_rw ( float , f"{prefix}/{setpoint_suffix}")
            self.readback = tango_signal_r(float, f"{prefix}/{readback_suffix}")

        super().__init__(name=name, **kwargs)

    async def stop(self, success=True) -> SyncOrAsync[None]:
        self._set_success = success

    @AsyncStatus.wrap
    async def stage(self) -> None:
         print("Staging power converter: get future ")
         st = super().stage()
         print("Staging power converter: await future ")
         r =  await st
         print("Staging power converter: return result")
         return  r

    # async def unstage(self) -> None:
    #    print("Untaging power converter: get future ")
    #     st = super().stage()
    #    print("Unstaging power converter: await future ")
    #    r =  await st
    #    print("Unstaging power converter: return result")
    #    return  r




async def run_device():
    pc = Powerconverter(
        prefix="SimpleTangoServer/test/power_converter_Q3P2T6R",
        setpoint_suffix="current_setpoint",
        readback_suffix="current_readback"
    )
    await pc.connect()
    await pc.stage()
    r = await pc.read()
    print(r)
    await pc.unstage()



def main():

    cat = catalog["heavy_local"]
    pc = Powerconverter(
        prefix="SimpleTangoServer/test/power_converter_Q3P2T6R",
        setpoint_suffix="current_setpoint",
        readback_suffix="current_readback"
    )

    async def connect():
        await pc.connect()
        print (await pc.read())

    RE = RunEngine()
    RE.subscribe(cat.v1.insert)
    asyncio.get_event_loop().run_until_complete(connect())
    uid, = RE(bpp.count([pc], 3))
    run = cat[uid]
    print(run)
    print(uid)
    time.sleep(3)


if __name__ == "__main__":
    asyncio.run(run_device())
    # main()