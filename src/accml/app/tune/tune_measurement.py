import asyncio
import os
from typing import Sequence, Union

from accml.core.interfaces.device_interface import SimpleDevice, SimpleMovable
from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml.core.model.command import Command, BehaviourOnError, CommandSequence
from accml.custom.epics.mexec_simple.power_converter import SimplePowerConverter
from accml.custom.epics.mexec_simple.tunes import Tunes

def setup_devices(quadrupole_pc_names: Sequence[str]) -> Union[SimpleDevice, SimpleMovable]:
    prefix = os.environ.get("USER", 'Anonym') + ":"
    tunes = Tunes(prefix=f"{prefix}TUNECC", name="tune")
    quadrupole_pcs = {
        name: SimplePowerConverter(name=name, prefix=f"{prefix}{name}") for name in quadrupole_pc_names
    }
    return dict(
        tunes=tunes,
        quadrupole_pcs=quadrupole_pcs
    )



def tune(*, quadrupole_pc_names: Sequence[str], measurement_values: Sequence[float],
         mexec: MeasurementExecutionEngine = None,
         info_signals
         ):
    cmds_on_machine = []
    for name in quadrupole_pc_names:
        for val in measurement_values:
            cmds_on_machine.append(
                Command(id=name, property="delta_set_current", value=val, behaviour_on_error=BehaviourOnError.stop)
            )

    # this functions should be external to this instrument
    devices = setup_devices(quadrupole_pc_names=quadrupole_pc_names)
    cmds_on_machine = CommandSequence(commands=cmds_on_machine)

    # extract the device id's that the commands work on
    device_ids = set([cmd.id for cmd in cmds_on_machine.commands])

    # inform setup on which devices are actually needed
    # so setup could select only to instantiate those devices
    # before returning it should check that it can handle all mentioned devices

    # TODO: should be handled internally, needs to be overridden ?
    actuators = {name: pc for name, pc in devices["quadrupole_pcs"].items()}
    # used so that it is easier to see what is happening
    # could be included in the standard software multiplexer

    mexec.setup()
    md = {}

    uid = mexec.execute(
        commands=cmds_on_machine.commands,  # need to add bpms
        detectors=[devices["tunes"]],
        actuators=actuators,
        md=md,
    )
    print(f"Run created {uid=}")
