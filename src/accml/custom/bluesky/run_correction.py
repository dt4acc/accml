"""bluesky plans for running a correction in an infinte loop

Todo:
    remove dependencies on Tune device.
    Tune Device should return a data model

"""
import logging
import itertools
from typing import Sequence, Dict, Union

from ophyd_async.core import Device, SignalRW
import bluesky.preprocessors as bpp
import bluesky.plan_stubs as bps

# Todo: fix this dependency problem
from accml.app.tune.tune_correction_controller import (
    compute_stat_for_transactional_command,
    correction_action_to_commands,
)
from .plans import (
    transactional_actuator_commands_plan,
    retrieve_reference_state_plan,
    extract_current_state_probe_commands,
    rework_delta_commands,
)
from accml_lib.core.bl.delta_backend import StateCache
from accml_lib.core.interfaces.solver.oracle import Oracle
from accml_lib.core.interfaces.solver.policy import PolicyBase
from accml_lib.core.model.command import Command, TransactionCommand
from accml_lib.core.model.tune import Tune

logger = logging.getLogger("accml")


def corrections_plan(
    *,
    oracle: Oracle,
    policy: PolicyBase,
    detectors: Sequence[Device],
    actuators: Dict[str, Device],
    set_commands: Dict[str, Command],
    info_signals: Dict[str, SignalRW],
    cache: StateCache,
    md: Dict,
    **kwargs,
):
    """Translate commands to bluesky run-engine messages"""
    _md = md or dict()
    # CommandSequence nor Commands is json serializable ....
    _md.update(dict(oracle=repr(oracle), policy=repr(policy)))

    @bpp.stage_decorator(
        [sig for _, sig in info_signals.items()]
        + list(detectors)
        + list(actuators.values())
    )
    @bpp.run_decorator(md=_md)
    def inner():
        # first ... load cache with reference state
        yield from retrieve_reference_state_plan(
            commands=extract_current_state_probe_commands(
                [cmd for _, cmd in set_commands.items()]
            ),
            detectors=detectors,
            actuators=actuators,
            cache=cache,
        )

        r = yield from run_corrections_commands_plan(
            oracle=oracle,
            policy=policy,
            detectors=detectors,
            set_commands=set_commands,
            actuators=actuators,
            info_signals=info_signals,
            cache=cache,
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
    cache: StateCache,
    n_readings: int,
    info_signals: Dict[str, SignalRW],
    wait_before_read: float = 0,
    delay: float = 0,
    n_steps: Union[int, None] = None,
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
        current_state = None
        if n_steps is not None and cnt >= n_steps:
            logger.info("Terminating control loop at step %s", cnt)
            return
        # presumably set some value already ...
        yield from bps.wait()
        if wait_before_read > 0e0:
            yield from bps.sleep(wait_before_read)
        for i in range(n_readings):
            if i > 0 and delay > 0:
                yield from bps.sleep(delay)
            current_state = yield from bps.trigger_and_read(all_detectors)

        assert (
            current_state is not None
        ), "no current state read, can not process further"
        # Todo: the device can not return the model but only a dict
        #       this is required for databroker serialisation
        #       oracle could happily work with a dictionary too
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

        t_cmds = rework_delta_commands(commands=t_cmd.transaction, cache=cache)
        yield from transactional_actuator_commands_plan(
            transactional_commands=[TransactionCommand(transaction=t_cmds)],
            detectors=detectors,
            actuators=actuators,
            cache=cache,
            num_readings=0,
        )


__all__ = ["corrections_plan"]
