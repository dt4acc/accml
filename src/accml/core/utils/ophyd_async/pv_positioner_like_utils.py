import asyncio
import numpy as np
from bluesky.protocols import Movable, Stoppable, SyncOrAsync, Stageable
from ophyd_async.core import (
    StandardReadable,
    observe_value,
    WatcherUpdate,
    WatchableAsyncStatus,
)
from ophyd_async.epics.core import epics_signal_r, epics_signal_rw


class _SettableControllingDifference(StandardReadable, Movable, Stoppable, Stageable):
    """A power converter abstraction

    Checking that setpoint and readback correspond
    """

    _set_success = True

    def __init__(self, *args, **kwargs):
        self.eps_rel = kwargs.pop("eps_rel", 6e-2)
        self.eps_abs = kwargs.pop("eps_abs", 1e-2)
        super().__init__(*args, **kwargs)

    @WatchableAsyncStatus.wrap
    async def set(self, new_position: float, timeout: float = 2.0):
        # The move should complete successfully unless stop(success=False) is called
        self._set_success = True
        # Get some variables for the progress bar reporting
        old_position, units, precision = await asyncio.gather(
            self.setpoint.get_value(),
            self.units.get_value(),
            self.precision.get_value(),
        )
        await self.setpoint.set(new_position, wait=False)
        async for current_position in observe_value(
            self.readback, done_timeout=timeout
        ):
            # Emit a progress bar update
            yield WatcherUpdate(
                current=current_position,
                initial=old_position,
                target=new_position,
                name=self.name,
                unit=units,
                precision=precision,
            )
            # If we are at the desired position the break
            if np.isclose(
                current_position, new_position, atol=self.eps_abs, rtol=self.eps_rel
            ):
                break
        # If we were told to stop and report an error then do so
        if not self._set_success:
            raise RuntimeError("Motor was stopped")

    def stop(self, success=True) -> SyncOrAsync[None]:
        self._set_success = success

    async def connect(self, *args, **kwargs) -> None:
        stat = super().connect()
        r = await stat
        return r


class _ResettingDevice(_SettableControllingDifference):
    """
    WARNING:
            unstested code!
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.reference_value = kwargs.get("reference_value", None)
        self.timeout = kwargs.get("timeout", 20)
        self.settle_time = kwargs.get("settle_time", 0.5)
        self.set_back = kwargs.get("set_back", False)

    async def set_to_stored_value(self):
        if self.set_back and self.reference_value is not None:
            val = self.reference_value
            return await self.setpoint.set(self.reference_value)

    async def stage(self):
        """ """
        self.reference_value = await self.setpoint.get()
        return super().stage()

    def unstage(self):
        """

        Warning:
            If the call to super is not here proper plans will stop
            working at the second iteration
        """
        return super().unstage()

    async def stop(self, success=False):
        return self.set_to_stored_value()


class PVPositionerIsClose(_SettableControllingDifference):
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
            self.setpoint  = epics_signal_rw ( float , f"ca://{prefix}{setpoint_suffix}"     , name="set"  )
            self.readback  = epics_signal_r  ( float , f"ca://{prefix}{readback_suffix}"     , name="rdbk" )
            self.units     = epics_signal_r  ( str   , f"ca://{prefix}{readback_suffix}.EGU",  name="units")
            self.precision = epics_signal_r  ( int   , f"ca://{prefix}{readback_suffix}.PREC", name="prec" )
            # fmt:on

        super().__init__(name=name, **kwargs)



