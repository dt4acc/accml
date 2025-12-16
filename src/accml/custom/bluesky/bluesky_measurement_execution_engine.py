"""Demonstrator of a measurement execution engine

Todo:
    * implement full functionality

Missing features:

* handling behaviour_on_error
* how much of the accelerator access to wrap?
* hide devices behind a software multiplexer?
  In its current form quite some information will be stored
  in the databroker

"""
import functools
from dataclasses import asdict
from typing import Sequence, Dict

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky import RunEngine
from ophyd_async.core import Device, Signal

from ...core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from ...core.model.command import Command


def commands_plan(
        commands: Sequence[Command],
        detectors: Sequence[Device],
        actuators: Dict[str, Device],
        info_signals: Dict[str, Signal],
        *,
        num_readings: int
):
    """

    Inner plan for :func:`commands_execution_plan`

    Todo:
        Implement stop, ignore, rollback etc
        Device replace by ophyd_async.Settable
        info_signals as dataclass?
    """
    all_dev = list(info_signals.values()) + list(detectors) + list(actuators.values())
    dev_name = info_signals["device_name"]
    ch_name = info_signals["channel_name"]
    ch_val = info_signals["channel_value"]
    for command in commands:
        # first select the device
        t_device = actuators[command.id]
        channel = getattr(t_device, command.property)
        # then apply it to all
        yield from bps.mv(
            dev_name,
            str(command.id),
            ch_name,
            str(command.property),
            ch_val,
            command.value,
            channel,
            command.value,
        )
        # TODO: revisit how to address reading detectors
        #       also in the command language
        # read all devices
        yield from bps.wait()  # << required
        # optional: give hardware / twin time
        yield from bps.sleep(1)
        yield from bps.repeat(functools.partial(bps.trigger_and_read, all_dev), num=num_readings)


def commands_execution_plan(
        commands: Sequence[Command],
        detectors: Sequence[Device],
        actuators: Dict[str, Device],
        info_signals: Dict[str, Signal],
        md: None,
        **kwargs,
):
    """Translate commands to bluesky run-engine messages"""
    _md = md or dict()
    # CommandSequence nor Commands is json seriazable ....
    _md.update(dict(commands=[asdict(cmd) for cmd in commands]))

    @bpp.stage_decorator(list(detectors) + list(actuators.values()))
    @bpp.run_decorator(md=_md)
    def inner():
        r = yield from commands_plan(
            commands=commands,
            detectors=detectors,
            actuators=actuators,
            info_signals=info_signals,
            **kwargs
        )
        return r

    r = yield from inner()
    return r


class BlueskyMeasurementExecutionEngine(MeasurementExecutionEngine):
    """Demonstrator of a measurement engine as a bluesky runengine"""

    def __init__(self, run_engine: RunEngine):
        """

        Todo:
            Specify the device type
        """
        self.run_engine = run_engine

    def execute(
            self,
            commands_collection: Sequence[Sequence[Command]],
            detectors: Sequence[Device],
            actuators: Dict[str, Device],
            info_signals: Dict[str, Signal],
            md: Dict[str, object],
            **kwargs
    ) -> str:
        plan = commands_execution_plan(
            commands=commands_collection,
            detectors=detectors,
            actuators=actuators,
            info_signals=info_signals,
            md=md,
            **kwargs
        )
        (uid,) = self.run_engine(plan)
        return uid
