"""bluesky plans for running a correction in an infinte loop

Todo:
    remove dependencies on Tune device.
    Tune Device should return a data model

"""
import logging
import itertools
from typing import Sequence, Dict

from ophyd_async.core import Device, SignalRW
import bluesky.preprocessors as bpp
import bluesky.plan_stubs as bps

from accml.app.tune.model import Tune
from accml.app.tune.tune_correction_controller import (
    compute_stat_for_transactional_command,
    correction_action_to_commands,
)
from accml.core.model.command import Command
from accml.custom.bluesky.plans import transactional_actuator_commands_plan
from accml.core.interfaces.solver.oracle import Oracle
from accml.core.interfaces.solver.policy import PolicyBase

logger = logging.getLogger("accml")


def corrections_plan(
    *,
    oracle: Oracle,
    policy: PolicyBase,
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    set_commands: Dict[str, Command],
    info_signals: Dict[str, SignalRW],
    md: Dict,
    **kwargs,
):
    """Translate commands to bluesky run-engine messages"""
    _md = md or dict()
    # CommandSequence nor Commands is json seriazable ....
    _md.update(dict(oracle=repr(oracle), policy=repr(policy)))

    @bpp.stage_decorator(
        [sig for _, sig in info_signals.items()]
        + list(detectors)
        + list(actuators.values())
    )
    @bpp.run_decorator(md=_md)
    def inner():
        r = yield from run_corrections_commands_plan(
            oracle=oracle,
            policy=policy,
            detectors=detectors,
            set_commands=set_commands,
            actuators=actuators,
            info_signals=info_signals,
            **kwargs,
        )
        return r

    r = yield from inner()
    return r


def run_corrections_commands_plan(
    *,
    oracle: Oracle,
    policy: PolicyBase,
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    set_commands: Dict[str, Command],
    n_readings: int,
    info_signals: Dict[str, SignalRW],
    wait_before_read: float = 0,
    delay: float = 0,
):
    """

    Inner plan for :func:`transactional_commands_sequence_execution_plan`

    Todo:
        Implement stop, ignore, rollback etc
        Device replace by ophyd_async.Settable
        info_signals as dataclass?

        combine set_commands and actuators in a structure?
    """

    assert (
        wait_before_read >= 0e0
    ), f"wait before read must be >=0 but was {wait_before_read}"
    assert (
        n_readings >= 1
    ), f"detectors must be read at least once per turn, but was {n_readings}"
    all_detectors = [sig for _, sig in info_signals.items()] + list(detectors)

    counter = itertools.count()

    for cnt in counter:
        # presumably set some value already ...
        yield from bps.wait()
        if wait_before_read > 0e0:
            yield from bps.sleep(wait_before_read)
        for i in range(n_readings):
            if i > 0 and delay > 0:
                yield from bps.sleep(delay)
            current_state = yield from bps.trigger_and_read(all_detectors)

        # Todo: the device should return already a data model ...
        t_tune = Tune(**current_state["tune-transversal"]["value"])
        diff, correction_action = oracle.ask(t_tune)
        pca = policy.step(
            current_state=current_state, diff=diff, step=correction_action
        )
        t_cmd = correction_action_to_commands(pca, set_commands)
        stat_cmd = compute_stat_for_transactional_command(t_cmd)
        logger.info(
            "tune diff %s, cmd %s",
            diff,
        )
        yield from bps.mv(
            info_signals["tune-x-delta"],
            diff.x,
            info_signals["tune-y-delta"],
            diff.y,
            info_signals["applied-mean"],
            stat_cmd.mean,
            info_signals["applied-std"],
            stat_cmd.std,
            info_signals["applied-min"],
            stat_cmd.min,
            info_signals["applied-max"],
            stat_cmd.max,
        )

        yield from transactional_actuator_commands_plan(
            transactional_commands=[t_cmd],
            detectors=detectors,
            actuators=actuators,
            num_readings=0,
        )


__all__ = ["corrections_plan"]
