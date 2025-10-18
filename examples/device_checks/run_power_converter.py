import asyncio
import logging
import time


logging.basicConfig(level=logging.WARNING)

from ophyd_async.core import StandardReadable, AsyncStatus, AsyncStageable
from ophyd_async.tango.core import  tango_signal_r, tango_signal_rw
from bluesky.protocols import Movable, Stoppable, SyncOrAsync, Stageable, Reading
from bluesky import RunEngine
import bluesky.plans as bpp
# from databroker import catalog
from ophyd_async.tango.core import TangoReadable

from typing import Annotated as A
from ophyd_async.core import DEFAULT_TIMEOUT, AsyncStatus, SignalR, SignalRW, SignalX
from ophyd_async.core import StandardReadableFormat as Format
from ophyd_async.tango.core import TangoPolling


class Powerconverter(TangoReadable):
    current_setpoint: A[SignalRW[float], Format.HINTED_SIGNAL, TangoPolling(1.0, 0.1, 0.1)]
    current_readback: A[SignalR[float], Format.CONFIG_SIGNAL, TangoPolling(0.1, 0.1, 0.1)]


class Powerconverter2(TangoReadable):
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

        # with self.add_children_as_readables():
            # Todo: add hints
            # fmt:off
        self.setpoint = tango_signal_rw(float , f"{prefix}/{setpoint_suffix}", name=f"{prefix}-setp")
        self.readback = tango_signal_r(float, f"{prefix}/{readback_suffix}", name=f"{prefix}-rdbk")
        self.add_readables([self.setpoint, self.readback])
        super().__init__(name=name, **kwargs)

    # async def stop(self, success=True) -> SyncOrAsync[None]:
    #     self._set_success = success

    # async def read(self) -> dict[str, Reading]:
    #    d = (await self.readback.read()).copy()
    #    d.update(await self.setpoint.read())
    #    return d

    # @AsyncStatus.wrap
    # async def stage(self) -> None:
    #      print("Staging power converter: get future ")
    #
    #     # await self.setpoint.stage()
    #     # await self.readback.stage()
    #
    #     st = super().stage()
    #     print("Staging power converter: await future ")
    #     r =  await st
    #     print("Staging power converter: return result")
    #     return  r
    #
    # async def unstage(self) -> None:
    #     print("Untaging power converter: get future ")
    #     st = super().stage()
    #     print("Unstaging power converter: await future ")
    #     r =  await st
    #     print("Unstaging power converter: return result")
    #     return  r




async def run_device():
    pc = Powerconverter(
        trl="SimpleTangoServer/test/power_converter_Q3P2T6R",
        # setpoint_suffix="current_setpoint",
        # readback_suffix="current_readback"
    )
    await pc.connect()
    await pc.stage()
    r = await pc.read()
    print(r)
    await pc.unstage()



def main():

    #cat = catalog["heavy_local"]
    pc = Powerconverter(
        name="pc",
        trl="SimpleTangoServer/test/power_converter_Q3P2T6R",
        # setpoint_suffix="current_setpoint",
        # readback_suffix="current_readback"
    )

    async def connect():
        await pc.connect()
        pc.stage()
        print (await pc.read())

    asyncio.run(connect())

    RE = RunEngine()
    # RE.subscribe(cat.v1.insert)
    uid, = RE(bpp.count([pc], 3))
    # run = cat[uid]
    # print(run)
     #print(uid)
    # time.sleep(3)


if __name__ == "__main__":
    # asyncio.run(run_device())
    main()