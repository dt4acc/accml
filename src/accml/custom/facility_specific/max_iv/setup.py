import os


from accml.custom.tango.devices.power_converter import PowerConverter
from accml.custom.tango.devices.master_clock import MasterClock
from accml.custom.tango.devices.tunes import Tunes
from accml.core.interfaces.devices_facade import DevicesFacade
from accml.core.utils.ophyd_async.multiplexer_for_settable_devices import MultiplexerProxy
from .liasion_translator_setup import load_managers



def setup() -> DevicesFacade:
    prefix = os.environ.get("USER", "Anonym") + ":"
    yp, _, __ = load_managers()

    quad_pcs = {
        name: PowerConverter(
            trl="R1/MAG/PSDH-01",
            name=name,
            readback_name="current_readback",
            setpoint_name="current_setpoint",
        )
        for name in yp.get("quadrupole_pcs")
    }

    quadrupoles = MultiplexerProxy(
        name="quad_col", settable_devices=quad_pcs, default_name=list(quad_pcs)[0]
    )

    master_clock = MasterClock("R1/MAG/master_clock", name="mc")
    tunes = Tunes("R1/MAG/tune_device", name="tune")
    return dict(quadrupole_pcs=quadrupoles, master_clock=master_clock, tunes=tunes)


if __name__ == "__main__":
    d = setup()
    d