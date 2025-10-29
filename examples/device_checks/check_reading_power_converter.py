import asyncio
import logging
from typing import Annotated as A

logging.basicConfig(level=logging.WARNING)

from ophyd_async.core import (
    derived_signal_rw,
    AsyncStageable,
    AsyncStatus,
    SignalR,
    SignalRW,
    StandardReadableFormat as Format,
)
from ophyd_async.tango.core import TangoPolling, TangoReadable

from bluesky import RunEngine
import bluesky.plans as bpp
from databroker import catalog


class PowerconverterBase(TangoReadable, AsyncStageable):
    def __init__(self, trl: str | None = "", name="", *, set_signal_name: str):
        super().__init__(trl, name=name)
        self._ref_current = None
        # current tango version: signals are the names of the properties of the
        # tango device. These have to be set accordingly

        self._set_signal = getattr(self, set_signal_name)
        self.diff_current = derived_signal_rw(
            self._to_relative_current,
            self._set_diff_current,
            current=self._set_signal,
            derived_precision=5,
        )
        self.add_readables([self.diff_current])

    def _to_relative_current(self, current: float) -> float:
        assert (
            self._ref_current is not None
        ), "reference current None, was device staged?"
        r = current - self._ref_current
        self.log.debug(
            f"Computing relative current {current} - {self._ref_current}-> {r}"
        )
        return r

    async def _set_diff_current(self, dv: float):
        current = dv + self._ref_current
        self.log.debug(f"Setting {dv=} -> {current=}")
        await self._set_signal.set(current)
        if self.log.getEffectiveLevel() >= logging.DEBUG:
            rdbk = await self._set_signal._cache.backend.get_value()
            setp = await self._set_signal._cache.backend.get_setpoint()
            self.log.debug(f"Setting {dv=} -> {current=}: {setp=}, {rdbk=}")

    async def read(self):
        """
        Todo:
            need to find out why I have to call read explicitly
        """
        d = await super().read()
        entry = d[self._set_signal.name]
        d[self.diff_current.name] = dict(
            value=self._to_relative_current(entry["value"]),
            timestamp=entry["timestamp"],
        )
        return d

    @AsyncStatus.wrap
    async def stage(self) -> None:
        self.log.info("staging")
        r = await super().stage()
        self._ref_current = await self._set_signal.get_value()
        return r

    @AsyncStatus.wrap
    async def unstage(self) -> None:
        self.log.info("unstaging")
        r = await super().unstage()
        self._ref_current = None
        return r


class Powerconverter(PowerconverterBase):
    """
    Todo:
        need to find out why signals must be marked as uncached...
    """

    # fmt: off
    current_setpoint: A[ SignalRW[float] , Format.HINTED_UNCACHED_SIGNAL, TangoPolling(1.0, 0.01, 1e-4) ]
    current_readback: A[ SignalR[float] ,  Format.UNCACHED_SIGNAL,        TangoPolling(1.0, 0.01, 1e-4) ]
    # fmt: on


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
    # need some catalog so that I can read back the data
    cat = catalog["heavy_local"]
    pc = Powerconverter(
        name="pc",
        trl="SimpleTangoServer/test/power_converter_Q3P2T6R",
        set_signal_name="current_setpoint",
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
    (uid,) = RE(bpp.list_scan([pc], pc.diff_current, [0, 1, -1, 0]))
    run = cat[uid]
    print(run.primary.read())


if __name__ == "__main__":
    # you can only run one at once
    # asyncio.run(run_device())
    main()
