import asyncio
from typing import Dict

from accml.app.tune.oracle import TuneOracle
from accml.app.tune.policy import TunePolicy
from accml.core.interfaces.devices_facade import DevicesFacade
from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml.core.model.command import Command, BehaviourOnError

from .model import TuneResponseCollection, Tune


def tune_correction(dm: TuneResponseCollection, devices: DevicesFacade, mexec: MeasurementExecutionEngine):
    """

    """

    oracle = TuneOracle(
        x=TuneResponseCollection(col=[item for item in dm.col if item.pc_name[:2] == "Q4"]),
        y=TuneResponseCollection(col=[item for item in dm.col if item.pc_name[:2] == "Q3"]),
        reference=Tune(x=1060, y=907)
    )
    policy = TunePolicy()

    # measure the current state
    current_state = Tune(x=1065, y=905)
    diff_tune, r = oracle.ask(current_state)
    r = policy.step(current_state, diff_tune, r)


    commands = [Command(id=pc_name, property="delta_set_current", value=dI, behaviour_on_error=BehaviourOnError.stop) for pc_name, dI in r.items()]
    actuators = {cmd.id : devices.get("quadrupole_pcs").settable_devices.get(cmd.id) for cmd in commands}

    tunes = devices["tunes"]
    quadrupole_pcs = devices["quadrupole_pcs"]

    async def connect():
        await tunes.connect(timeout=2.0)
        await quadrupole_pcs.connect(timeout=2.0)

    asyncio.run(connect())


    uid = mexec.execute(
        # This command should be executed in one shot
        commands_collection=[commands],  # need to add bpms
        detectors=[devices.get("tunes")],
        actuators=actuators,
        info_signals=None,
        md={},
        num_readings=2,
    )
