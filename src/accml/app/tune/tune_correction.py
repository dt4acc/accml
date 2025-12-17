import asyncio
from typing import Dict

from accml.app.tune.oracle import TuneOracle
from accml.app.tune.policy import TunePolicy
from accml.core.interfaces.devices_facade import DevicesFacade
from accml.core.interfaces.measurement_execution_engine import (
    MeasurementExecutionEngine,
)
from accml.core.model.command import Command, BehaviourOnError, TransactionalCommand
from accml.custom.bluesky.plans import transactional_commands_sequence_execution_plan
from accml.custom.bluesky.run_correction import (
    run_corrections_commands_plan,
    corrections_plan,
)

from .model import TuneResponseCollection, Tune


def tune_correction(
    dm: TuneResponseCollection,
    devices: DevicesFacade,
    mexec: MeasurementExecutionEngine,
    info_signals,
):
    """

    Todo:

      * reference / target tune from caller
      * consider to provide fine tuning from the outside
      * only connect to the actuators actually required

    """

    oracle = TuneOracle(col=dm, target=Tune(x=1055, y=902))
    policy = TunePolicy(scale=1.0)

    actuators = {
        name: devices.get("quadrupole_pcs").settable_devices.get(name)
        for name in oracle.pc_names
    }
    print(" ".join([f"mfp:{pc_name}:set" for pc_name in oracle.pc_names]))
    tunes = devices["tunes"]
    quadrupole_pcs = devices["quadrupole_pcs"]

    async def connect():
        await tunes.connect(timeout=2.0)
        await quadrupole_pcs.connect(timeout=2.0)

    asyncio.run(connect())

    uid = mexec.execute(
        corrections_plan(
            oracle=oracle,
            policy=policy,
            detectors=[devices.get("tunes")],
            actuators=actuators,
            info_signals=info_signals,
            num_readings=2,
            wait_before_read=0.1,
            delay=0.1,
            md={},
        )
    )
    return uid
