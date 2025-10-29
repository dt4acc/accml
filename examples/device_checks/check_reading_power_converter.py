import asyncio
import logging

from typing import Annotated as A

from bluesky.protocols import Reading
from event_model import DataKey

logging.basicConfig(level=logging.WARNING)

from ophyd_async.tango.core import  tango_signal_r, tango_signal_rw
from ophyd_async.core import derived_signal_rw, AsyncStatus, Device, AsyncStageable

from bluesky import RunEngine
import bluesky.plans as bpp
from databroker import catalog
from ophyd_async.tango.core import TangoReadable, TangoDevice

from ophyd_async.core import SignalR, SignalRW
from ophyd_async.core import StandardReadableFormat as Format
from ophyd_async.tango.core import TangoPolling


class Powerconverter(TangoReadable, TangoDevice, AsyncStageable):
    """
    Todo:
        need to find out why signals must be marked as uncached...
        need to find out why only hinted signals end up in the output
    """
    current_setpoint: A[SignalRW[float], Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4)]
    current_readback: A[SignalR[float], Format.UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4)]

    def __init__(self, trl: str | None = "", name=""):
        super().__init__(trl, name=name)
        self._ref_current = None
        self.diff_current = derived_signal_rw(
            self._to_relative_current, self._set_diff_current, current=self.current_setpoint, derived_precision=5,
        )
        self.add_readables([self.diff_current], Format.UNCACHED_SIGNAL)

    def _to_relative_current(self, current: float) -> float:
        assert self._ref_current is not None, "reference current None, was device staged?"
        r = current - self._ref_current
        self.log.debug(f"Computing relative current {current} - {self._ref_current}-> {r}")
        return r

    async def _set_diff_current(self, dv: float):
        current  = dv + self._ref_current
        self.log.debug(f"Setting {dv=} -> {current=}")
        await self.current_setpoint.set(current)
        return
        rdbk = await self.current_setpoint._cache.backend.get_value()
        setp = await self.current_setpoint._cache.backend.get_setpoint()
        self.log.debug(f"Setting {dv=} -> {current=}: {setp=}, {rdbk=}")

    @AsyncStatus.wrap
    async def stage(self) -> None:
        self.log.info("staging")
        r = await super().stage()
        # todo: set it with actual current
        self._ref_current = await self.current_setpoint.get_value()
        return r

    @AsyncStatus.wrap
    async def unstage(self) -> None:
        self.log.info("unstaging")
        r = await super().unstage()
        self._ref_current = None
        return r

    async def describe(self) -> dict[str, DataKey]:
        """

        Todo:
            need to find out why I have to add that here
            is an uncached signal arriving here
        """
        d = await super().describe()
        return d

    async def read(self) -> dict[str, Reading]:
        """

        Todo:
            need to find out how I need to configure the derived signal so that it will
            be always read out
        """
        d = await super().read()
        return d
        src_name = self.current_setpoint.name
        dst_name = self.diff_current.name
        r = d.get(src_name)
        d[dst_name] = Reading(value=self._to_relative_current(r.get("value")), timestamp=r.get("timestamp"))
        return d

async def run_device():
    pc = Powerconverter(
        name="pc",
        trl="SimpleTangoServer/test/power_converter_Q3P2T6R",
    )
    t = await pc.connect()
    t
    await pc.stage()
    d = await pc.describe()
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
    # uid, = RE(bpp.count([pc], 3))
    # run = cat[uid]
    # print(run.primary.read())
    uid, = RE(bpp.scan([pc], pc.diff_current, 0, 1, 3))
    run = cat[uid]
    print(run.primary.read())


if __name__ == "__main__":
    # you can only run one at once
    # asyncio.run(run_device())
    main()