#!/usr/bin/env python3
import asyncio
import numpy as np

from bluesky import RunEngine
from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp

from bluesky.protocols import Movable, Stoppable, SyncOrAsync, Stageable
from ophyd_async.core import (
    StandardReadable,
    observe_value,
    WatcherUpdate,
    WatchableAsyncStatus,
)
from ophyd_async.tango.core import tango_signal_rw, tango_signal_r


class PVPositionerIsClose(StandardReadable, Movable, Stoppable, Stageable):
    """Minimal Tango positioner."""

    _set_success = True

    def __init__(
        self,
        prefix: str,
        *,
        setpoint_suffix: str,
        readback_suffix: str,
        name: str = "",
        eps_rel: float = 6e-2,
        eps_abs: float = 1e-2,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.eps_rel = eps_rel
        self.eps_abs = eps_abs

        with self.add_children_as_readables():
            self.setpoint = tango_signal_rw(
                float,
                f"{prefix}/{setpoint_suffix}",
                f"{prefix}/{setpoint_suffix}",  # ✅ correct mapping
                name="set",
            )
            self.readback = tango_signal_r(
                float,
                f"{prefix}/{readback_suffix}",
                name="rdbk",
            )

    async def connect(self, *args, **kwargs):
        await super().connect(*args, **kwargs)
        await asyncio.gather(
            self.setpoint.get_value(),
            self.readback.get_value(),
        )

    @WatchableAsyncStatus.wrap
    async def set(self, new_position: float, timeout: float = 2.0):
        self._set_success = True
        old_position = await self.readback.get_value()
        await self.setpoint.set(new_position)
        async for current_position in observe_value(self.readback, done_timeout=timeout):
            yield WatcherUpdate(
                current=current_position,
                initial=old_position,
                target=new_position,
                name=self.name,
                unit="",
                precision=3,
            )
            if np.isclose(current_position, new_position, atol=self.eps_abs, rtol=self.eps_rel):
                break
        if not self._set_success:
            raise RuntimeError("Move aborted via stop()")

    def stop(self, success=True) -> SyncOrAsync[None]:
        self._set_success = success


class PowerConverter(PVPositionerIsClose):
    def __init__(self, prefix: str, name: str):
        super().__init__(
            prefix=prefix,
            setpoint_suffix="current_setpoint",
            readback_suffix="current_readback",
            name=name,
        )


# ----------------------------
# Proper Bluesky plan with run context
# ----------------------------
def one_read_plan(dev):
    """Stage → trigger_and_read → unstage inside a run."""
    @bpp.stage_decorator([dev])
    @bpp.run_decorator(md={"purpose": "tango test"})   # ✅ ensures open_run / close_run
    def _inner():
        yield from bps.trigger_and_read([dev])
    return _inner()


async def main():
    prefix = "SimpleTangoServer/test/power_converter_Q5PT3R"
    pc = PowerConverter(prefix=prefix, name="pc_Q5PT3R")

    await pc.connect()
    sp = await pc.setpoint.get_value()
    rb = await pc.readback.get_value()
    print(f"Initial: setpoint={sp}, readback={rb}")

    # Try a small move
    try:
        await pc.set(rb + 0.5, timeout=3.0)
    except Exception as exc:
        print(f"Non-fatal: move timed/aborted: {exc!r}")

    # Force manual read if no update events
    await asyncio.sleep(0.5)
    rb_force = await pc.readback.get_value(cached=False)
    print(f"Manual readback check: {rb_force}")


    # Run a real Bluesky plan
    RE = RunEngine({})
    uid = RE(one_read_plan(pc))
    print(f"Run complete, uid={uid}")

    sp2 = await pc.setpoint.get_value()
    rb2 = await pc.readback.get_value()
    print(f"Final: setpoint={sp2}, readback={rb2}")


if __name__ == "__main__":
    asyncio.run(main())
