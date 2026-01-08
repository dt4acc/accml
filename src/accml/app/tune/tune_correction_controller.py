import asyncio
import itertools
import logging
from typing import Dict, Sequence

import numpy as np

from accml.app.tune.model import CorrectionStat
from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml.core.interfaces.solver.oracle import Oracle
from accml.core.interfaces.solver.policy import PolicyBase
from accml.core.model.command import TransactionCommand, ReadCommand

logger = logging.getLogger("accml")


class TuneCorrectionController:
    def __init__(
            self,
            *,
            mexec: MeasurementExecutionEngine,
            oracle: Oracle,
            policy: PolicyBase,
            num_readings: int,
            wait_before_read: float,
            delay: float,
            logger = logger
    ):
        self.mexec = mexec
        self.oracle = oracle
        self.policy = policy
        self.num_readings = num_readings
        self.wait_before_read = wait_before_read
        self.delay = delay
        self.logger = logger

    async def one_step(self):
        pass

    async def continous(self, *, n_steps=None, read_commands: Sequence[ReadCommand]):
        counter = itertools.count()
        for cnt in counter:
            current_state = None
            if n_steps is not None and cnt >= n_steps:
                self.logger.info("Terminating control loop at step %s", cnt)
                return
            if self.wait_before_read > 0e0:
                await asyncio.sleep(self.wait_before_read)
            for i in range(self.num_readings):
                if i > 0 and self.delay > 0:
                    await asyncio.sleep(self.delay)
                await self.mexec.trigger(read_commands)
                current_state = await self.mexec.read(read_commands)

            assert current_state is not None, "No current_state were read, can't prcess further"
            # Todo: need to be more flexible here
            t_tune = current_state.get("tune-transversal").payload
            diff, correction_action = self.oracle.ask(t_tune)
            logger.warning("Read tune (from mexec) %s, diff %s", t_tune, diff)
            stat_oracle = compute_stat_for_oracle(correction_action)
            logger.warning("Oracle correction action %s +/- %s range: %s - %s",
                           stat_oracle.mean, stat_oracle.std, stat_oracle.min, stat_oracle.max)
            t_cmd = self.policy.step(current_state, diff, correction_action)
            stat_cmd = compute_stat_for_transactional_command(t_cmd)
            logger.warning("Applying action %s +/- %s range %s-%s",
                           stat_cmd.mean, stat_cmd.std, stat_cmd.min, stat_cmd.max)
            await self.mexec.set(t_cmd.transaction)


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