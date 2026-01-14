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
import asyncio
import functools
import itertools
from dataclasses import asdict
from typing import Sequence, Dict

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky import RunEngine
from ophyd_async.core import Device, Signal

from accml_lib.core.interfaces.devices_facade import DevicesFacade
from accml_lib.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml_lib.core.model.command import Command, ReadCommand, TransactionCommand
from accml_lib.core.model.result import ReadTogether


def commands_plan(
        commands: Sequence[TransactionCommand],
        detectors: Sequence[Device],
        actuators: Dict[str, Device],
        info_signals: Dict[str, Signal],
        n_readings: int
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
    for tc in commands:
        # only prepared for a single device currently
        command, = tc.transaction
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
        yield from bps.wait()
        # optional: give hardware / twin time
        yield from bps.sleep(1)
        yield from bps.repeat(functools.partial(bps.trigger_and_read, all_dev), num=n_readings)


def commands_execution_plan(
        commands: Sequence[TransactionCommand],
        detectors: Sequence[Device],
        actuators: Dict[str, Device],
        info_signals: Dict[str, Signal],
        n_readings: int,
        md: None,
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
            n_readings=n_readings,
        )
        return r

    r = yield from inner()
    return r


class BlueskyMeasurementExecutionEngine(MeasurementExecutionEngine):
    """Demonstrator of a measurement engine as a bluesky runengine"""

    def __init__(self, devices: DevicesFacade,  run_engine: RunEngine, info_signals: Sequence[Signal]):
        """

        Todo:
            Specify the device type
        """
        self.run_engine = run_engine
        self.devices = devices
        self.info_signals = info_signals

    def execute(
            self,
            commands_collection: Sequence[TransactionCommand],
            detectors: Sequence[ReadCommand],
            # actuators: Dict[str, Device],
            md: Dict[str, object],
            **kwargs,
    ) -> str:

        actuator_identifiers = extract_device_identifiers(commands_collection)

        actuators = {id_: self.devices.get(id_) for id_ in actuator_identifiers}
        dets = [self.devices.get(det.id) for det in detectors]

        loop = asyncio.get_event_loop()
        loop.run_until_complete(connect_to_devices(list(actuators.values()) + dets))

        plan = commands_execution_plan(
            commands=commands_collection,
            detectors=dets,
            actuators=actuators,
            info_signals=self.info_signals,
            md=md,
            **kwargs,
        )
        (uid,) = self.run_engine(plan)
        return uid

    async def set(self, cmds: Sequence[Command]):
        raise NotImplementedError("needs to be implemented")

    async def trigger_read(self, cmds: Sequence[ReadCommand]) -> ReadTogether:
        # signals = [getattr(self.devices.get(cmd.id), cmd.property) for cmd in cmds]
        # devices = [self.devices.get(cmd.id) for cmd in cmds]
        raise NotImplementedError("needs to be implemented")


def extract_device_identifiers(commands_collection: Sequence[TransactionCommand]) -> Sequence[str]:
    return list(itertools.chain(*[[cmd.id for cmd in tc.transaction] for tc in commands_collection]))


async def connect_to_devices(devices, timeout=5.0):
    """
    """
    return await asyncio.gather(
        *[dev.connect(timeout=timeout) for dev in devices]
    )
