import asyncio
import itertools
import logging
from typing import Dict, Sequence

import numpy as np

from accml.app.tune.interface import TuneControllerInterface
from accml_lib.core.interfaces.measurement_execution_engine import (
    MeasurementExecutionEngine,
)
from accml_lib.core.interfaces.solver.oracle import Oracle
from accml_lib.core.interfaces.solver.policy import PolicyBase
from accml_lib.core.model.command import (
    BehaviourOnError,
    Command,
    ReadCommand,
    TransactionCommand,
)
from accml_lib.core.model.tune import Tune, CorrectionStat

logger = logging.getLogger("accml")


class TuneCorrectionController(TuneControllerInterface):
    """A simple I type controller

    It only implements the integral part of the controller:
       i.e. react to the change

    """

    def __init__(
        self,
        *,
        mexec: MeasurementExecutionEngine,
        oracle: Oracle,
        policy: PolicyBase,
        num_readings: int,
        wait_before_read: float,
        delay: float,
        logger=logger
    ):
        assert num_readings >= 1, "need to do at least one reading per loop"
        self.mexec = mexec
        self.oracle = oracle
        self.policy = policy
        self.num_readings = num_readings
        self.wait_before_read = wait_before_read
        self.delay = delay
        self.logger = logger

    async def continuous(
        self,
        *,
        read_commands: Sequence[ReadCommand],
        set_commands: Sequence[Command],
        n_steps=None
    ):
        cmds = {cmd.id: cmd for cmd in set_commands}
        counter = itertools.count()
        for cnt in counter:
            if n_steps is not None and cnt >= n_steps:
                self.logger.info("Terminating control loop at step %s", cnt)
                return
            await self.one_step(read_commands, cmds)

    async def one_step(
        self, read_commands: Sequence[ReadCommand], set_commands: Dict[str, Command]
    ):
        current_state = None

        if self.wait_before_read > 0e0:
            await asyncio.sleep(self.wait_before_read)
        for i in range(self.num_readings):
            if i > 0 and self.delay > 0:
                await asyncio.sleep(self.delay)
            current_state = await self.mexec.trigger_read(read_commands)

        assert (
            current_state is not None
        ), "No current_state were read, can't process further"
        # Todo: need to be more flexible here...should be derived from read command
        t_tune = current_state.get("tune-transversal").payload
        pca = compute_correction_state(
            oracle=self.oracle,
            policy=self.policy,
            t_tune=t_tune,
            current_state={datum.name: datum.payload for datum in current_state.data},
            logger=logger,
        )
        t_cmd = correction_action_to_commands(pca, set_commands)

        stat_cmd = compute_stat_for_transactional_command(t_cmd)
        logger.warning(
            # Extra space to align with other logging output
            "Applying          action % .4f +/- % .4f range: % .4f -- % .4f",
            stat_cmd.mean,
            stat_cmd.std,
            stat_cmd.min,
            stat_cmd.max,
        )
        await self.mexec.set(t_cmd.transaction)


def compute_correction_state(
    *,
    oracle: Oracle,
    policy: PolicyBase,
    current_state: Dict[str, object],
    t_tune: Tune,
    logger
) -> Dict[str, float]:
    diff, correction_action = oracle.ask(t_tune)
    logger.warning("Read tune (from mexec) %s, diff %s", t_tune, diff)
    stat_oracle = compute_stat_for_oracle(correction_action)
    logger.warning(
        "Oracle correction action % .4f +/- % .4f range: % .4f -- % .4f",
        stat_oracle.mean,
        stat_oracle.std,
        stat_oracle.min,
        stat_oracle.max,
    )
    return policy.step(current_state, diff, correction_action)


def correction_action_to_commands(
    correction_actions: Dict[str, float], set_commands: Dict[str, Command]
) -> TransactionCommand:
    def create_command(name: str, value: float) -> Command:
        ref_cmd = set_commands[name]
        return Command(
            id=ref_cmd.id,
            property=ref_cmd.property,
            value=value,
            behaviour_on_error=BehaviourOnError.stop,
        )

    return TransactionCommand(
        transaction=[
            create_command(pc_name, value)
            for pc_name, value in correction_actions.items()
        ]
    )


def compute_stat_for_oracle(inp: Dict[str, float]) -> CorrectionStat:
    data = np.array([v for _, v in inp.items()])
    return CorrectionStat(
        mean=data.mean(), std=data.std(), min=data.min(), max=data.max()
    )


def compute_stat_for_transactional_command(inp: TransactionCommand) -> CorrectionStat:
    data = np.array([item.value for item in inp.transaction])
    return CorrectionStat(
        mean=data.mean(), std=data.std(), min=data.min(), max=data.max()
    )
