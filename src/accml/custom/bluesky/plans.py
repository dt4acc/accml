import functools
from dataclasses import asdict
from typing import Sequence, Dict

from accml.core.model.command import Command, TransactionCommand
from bluesky import plan_stubs as bps, preprocessors as bpp
from ophyd_async.core import Device, Signal


def transactional_commands_sequence_execution_plan(
    *,
    transaction_commands: Sequence[TransactionCommand],
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    md: Dict,
    **kwargs,
):
    """Excute transactional commands using bluesky plan stubs"""
    _md = md or dict()
    # CommandSequence nor Commands is json seriazable ....
    _md.update(dict(commands=[asdict(cmd) for cmd in transaction_commands]))

    @bpp.stage_decorator(list(detectors) + list(actuators.values()))
    @bpp.run_decorator(md=_md)
    def inner():
        r = yield from transactional_actuator_commands_plan(
            transaction_commands=transaction_commands,
            detectors=detectors,
            actuators=actuators,
            **kwargs,
        )
        return r

    r = yield from inner()
    return r


def transactional_actuator_commands_plan(
    *,
    transaction_commands: Sequence[TransactionCommand],
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    num_readings: int,
    wait_before_read: float = 0,
):
    """

    Inner plan for :func:`transactional_commands_sequence_execution_plan`

    Todo:
        Implement stop, ignore, rollback etc
        Device replace by ophyd_async.Settable
        info_signals as dataclass?
    """

    assert (
        wait_before_read >= 0e0
    ), f"wait before read must be >=0 but was {wait_before_read}"
    all_dev = list(detectors) + list(actuators.values())

    def prepare_transactional_move(transactional_command: Sequence[Command]):
        r = []
        for cmd in transactional_command:
            t_device = actuators[cmd.id]
            channel = getattr(t_device, cmd.property)
            r.extend([channel, cmd.value])
        return r

    for t_cmds in transaction_commands:
        # first select the device
        # then apply it to all
        yield from bps.mv(*prepare_transactional_move(t_cmds.transaction))
        # TODO: revisit how to address reading detectors
        #       also in the command language
        # read all devices
        yield from bps.wait()  # << required
        # optional: give hardware / twin time
        yield from bps.sleep(wait_before_read)
        #: todo: check behaviour if num_readings = 0
        yield from bps.repeat(
            functools.partial(bps.trigger_and_read, all_dev), num=num_readings
        )


def simple_command_sequence_execution_plan(
    *,
    commands: Sequence[Command],
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    info_signals: Dict[str, Signal],
    md: Dict,
    **kwargs,
):
    """Translate simple commands (i.e. only one device at a time) using bluesky plan stubs"""
    _md = md or dict()
    # CommandSequence nor Commands is json seriazable ....
    _md.update(dict(commands=[asdict(cmd) for cmd in commands]))

    @bpp.stage_decorator(list(detectors) + list(actuators.values()))
    @bpp.run_decorator(md=_md)
    def inner():
        r = yield from single_actuator_commands_plan(
            commands=commands,
            detectors=detectors,
            actuators=actuators,
            info_signals=info_signals,
            **kwargs,
        )
        return r

    r = yield from inner()
    return r


def single_actuator_commands_plan(
    *,
    commands: Sequence[Command],
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    info_signals: Dict[str, Signal],
    num_readings: int,
    wait_before_read: float = 0,
):
    """

    Inner plan for :func:`commands_execution_plan`

    Todo:
        Implement stop, ignore, rollback etc
        Device replace by ophyd_async.Settable
        info_signals as dataclass?
    """
    assert (
        wait_before_read >= 0e0
    ), f"wait before read must be >=0 but was {wait_before_read}"

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
        if wait_before_read > 0:
            yield from bps.sleep(wait_before_read)
        yield from bps.repeat(
            functools.partial(bps.trigger_and_read, all_dev), num=num_readings
        )


__all__ = [
    "simple_command_sequence_execution_plan",
    "transactional_commands_sequence_execution_plan",
]
