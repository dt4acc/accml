import os

from .liasion_translator_setup import load_managers
from accml.core.interfaces.devices_facade import DevicesFacade
from accml.core.utils.ophyd_async.multiplexer_for_settable_devices import (
    MultiplexerProxy,
)
from accml.custom.epics.devices.master_clock import MasterClock
from accml.custom.epics.devices.power_converter import PowerConverter
from accml.custom.epics.devices.tunes import Tunes

from .facility_specific_constants import special_pvs


def setup() -> DevicesFacade:
    prefix = os.environ.get("USER", "Anonym") + ":"
    yp, _, __ = load_managers()

    quad_pcs = {
        name: PowerConverter(
            f"{prefix}{name}:", name=name, readback_suffix="rdbk", setpoint_suffix="set"
        )
        for name in yp.get("quadrupole_pcs")
    }

    quadrupoles = MultiplexerProxy(
        name="quad_col", settable_devices=quad_pcs, default_name=list(quad_pcs)[0]
    )

    master_clock = MasterClock(f'{prefix}{special_pvs["master_clock"]}', name="mc")
    tunes = Tunes(f"{prefix}TUNECC", name="tune")
    return dict(quadrupole_pcs=quadrupoles, master_clock=master_clock, tunes=tunes)


if __name__ == "__main__":
    d = setup()
    d
