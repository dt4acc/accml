from typing import List
from ophyd_async.core import StandardReadable
from ophyd_async.tango.core import tango_signal_rw, tango_signal_r
class MasterClock(StandardReadable):
    """
    Tango-based master clock with setpoint/readback attributes.
    """
    def __init__(self, device: str, *, name: str = "mc",
                 set_attr: str = "frequency_setpoint",
                 rdbk_attr: str = "frequency_readback"):
        with self.add_children_as_readables():
            self.setpoint = tango_signal_rw(float, f"{device}/{set_attr}", name="ref_freq")
            self.readback = tango_signal_r (float, f"{device}/{rdbk_attr}", name="rdbk")
        super().__init__(name=name)
        self.set_frequency_at_start = None

    async def stage(self):
        r = await super().stage()
        # cache starting frequency for potential restore
        self.set_frequency_at_start = await self.setpoint.get_value()
        return r

    def unstage(self) -> List[object]:
        return super().unstage()
