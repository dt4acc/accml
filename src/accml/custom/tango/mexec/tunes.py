import time
from bluesky.protocols import Reading
from ophyd_async.core import StandardReadable, AsyncStatus
from ophyd_async.tango.core import tango_signal_rw, tango_signal_r


class TuneSignal(StandardReadable):
    def __init__(self, device: str, attribute: str, *, name: str):
        with self.add_children_as_readables():
            # Tango: device/attribute
            self.sig = tango_signal_r(float, f"{device}/{attribute}")
        super().__init__(name=name)

    @AsyncStatus.wrap
    async def read(self) -> dict[str, Reading]:
        # keep the “ensure a fresh value” semantics
        return await super().read()

class Tunes(StandardReadable):
    def __init__(self, device: str, *, name: str,
                 attr_x: str = "tune_x", attr_y: str = "tune_y"):
        with self.add_children_as_readables():
            self.x = TuneSignal(device, attr_x, name=f"{name}-x")
            self.y = TuneSignal(device, attr_y, name=f"{name}-y")
        super().__init__(name=name)
