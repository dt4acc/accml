import asyncio
from typing import Sequence

from accml.core.interfaces.devices_facade import DevicesFacade
from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml.core.model.command import Command, BehaviourOnError, CommandSequence


def tune(*, devices: DevicesFacade, quadrupole_pc_names: Sequence[str], measurement_values: Sequence[float],
         mexec: MeasurementExecutionEngine = None,
         info_signals
         ):
    cmds_on_machine = []
    for name in quadrupole_pc_names:
        for val in measurement_values:
            cmds_on_machine.append(
                Command(id=name, property="delta_set_current", value=val, behaviour_on_error=BehaviourOnError.stop)
            )

    cmds_on_machine = CommandSequence(commands=cmds_on_machine)

    # inform setup on which devices are actually needed
    # so setup could select only to instantiate those devices
    # before returning it should check that it can handle all mentioned devices
    tunes = devices["tunes"]
    quadrupole_pcs = devices["quadrupole_pcs"]

    async def connect():
        await tunes.connect(timeout=2.0)
        await quadrupole_pcs.connect(timeout=2.0)

    asyncio.run(connect())

    # TODO: should be handled internally, needs to be overridden ?
    actuators = {name: pc for name, pc in quadrupole_pcs.settable_devices.items()}
    # used so that it is easier to see what is happening
    # could be included in the standard software multiplexer

    md = {}

    uid = mexec.execute(
        commands_collection=cmds_on_machine.commands,  # need to add bpms
        detectors=[tunes],
        actuators=actuators,
        info_signals=info_signals,
        md=md,
        num_readings=2,
    )
    print(f"Run created {uid=}")
