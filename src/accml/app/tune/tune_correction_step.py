import asyncio
from typing import Sequence, Dict

from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine


def tune_correction_step(
        *,
        mexec: MeasurementExecutionEngine = None,
        oracle,
        targets,
        data_keys,
        quadrupole_pc_names: Sequence[str],
        info_signals,
        repeat_readings: int = 1,
        md = None
    ):
    """
    Todo:
        Do I need the quadrupole names: How I define which
        magnets are used? I think I should get the names list
        or querry yellow pages
    """

    _md = md or {}

    devices = mexec.setup()
    tunes = devices["tunes"]
    quadrupole_pcs = devices["quadrupole_pcs"]
    actuators = {name: pc for name, pc in quadrupole_pcs.settable_devices.items()}

    async def connect():
        await tunes.connect(timeout=2.0)
        await quadrupole_pcs.connect(timeout=2.0)

    asyncio.run(connect())

    uid = mexec.correction_step(
        oracle=oracle,
        policy=None,
        data_keys=data_keys,
        targets=targets,
        detectors=[tunes],
        actuators=actuators,
        info_signals=info_signals,
        md=_md,
    )
