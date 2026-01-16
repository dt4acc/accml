import asyncio
from typing import Sequence

from accml_lib.core.interfaces.utils.measurement_execution_engine import MeasurementExecutionEngine
from accml_lib.core.model.utils.command import ReadCommand, TransactionCommand, Command, CommandSequence, BehaviourOnError


def measure_tune_response(
    *,
    detectors: Sequence[ReadCommand],
    quadrupole_pc_names: Sequence[str],
    measurement_values: Sequence[float],
    mexec: MeasurementExecutionEngine = None,
    **kwargs
    ):
    """

    Todo:
        rename detectors to read_detectors? These are rather commands than
        real detectors
    """
    cmds_on_machine = []
    for name in quadrupole_pc_names:
        for val in measurement_values:
            cmds_on_machine.append(
                TransactionCommand(
                    transaction=[Command(id=name, property="delta_set_current", value=val, behaviour_on_error=BehaviourOnError.stop)]
                )
            )
    cmds_on_machine = CommandSequence(commands=cmds_on_machine)

    # inform setup on which devices are actually needed
    # so setup could select only to instantiate those devices
    # before returning it should check that it can handle all mentioned devices
    # tunes = devices["tunes"]
    #  quadrupole_pcs = devices["quadrupole_pcs"]



    # TODO: should be handled internally, needs to be overridden ?
    # actuators = {name: pc for name, pc in quadrupole_pcs.settable_devices.items()}
    # used so that it is easier to see what is happening
    # could be included in the standard software multiplexer

    md = {}

    uid = mexec.execute(
        detectors=detectors,
        commands_collection=cmds_on_machine.commands,  # need to add bpms
        **kwargs,
        # detectors=[tunes],
        # actuators=actuators,
        # info_signals=info_signals,
        md=md,
    )
    print(f"Run created {uid=}")
    return uid
