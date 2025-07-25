from bluesky.protocols import Movable, Status
from ophyd_async.core import AsyncStatus, StandardReadable


class NotInitalisedReferenceValue(AssertionError):
    """reference value not installed"""


class DiffChannel(StandardReadable, Movable):
    def __init__(self, *, name, parent):
        super().__init__(name=name)
        self.reference_value = None
        self.parent = parent

    @AsyncStatus.wrap
    async def stage(self):
        r = await super().stage()
        # Todo ... mangle it ...
        self.reference_value = await self.parent.setpoint.get_value()
        return r

    @AsyncStatus.wrap
    async def unstage(self):
        stat = await super().unstage()
        self.reference_value = None
        return stat

    @AsyncStatus.wrap
    async def set(self, diff_value) -> Status:
        assert (
            self.reference_value is not None,
            NotInitalisedReferenceValue("Power converter diff value was not set"),
        )
        value = diff_value + self.reference_value
        return self.parent.set(value)

