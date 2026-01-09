import asyncio
import logging
from typing import Sequence

from accml.core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from accml.core.interfaces.solver.oracle import Oracle
from accml.core.interfaces.solver.policy import PolicyBase
from accml.core.model.command import ReadCommand, Command
from accml.custom.bluesky.run_correction import corrections_plan

logger = logging.getLogger("accml")


class BlueskyTuneCorrectionController:
    def __init__(
            self,
            *,
            mexec: MeasurementExecutionEngine,
            oracle: Oracle,
            policy: PolicyBase,
            num_readings: int,
            wait_before_read: float,
            delay: float,
            logger = logger,
    ):
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
            n_steps=None,
    ):
        # Todo: fix me
        det_parents = [self.mexec.devices.get(cmd.id) for cmd in read_commands]
        detectors = [getattr(det_p, cmd.property) for det_p, cmd in zip(det_parents, read_commands)]
        actuators = {cmd.id: self.mexec.devices.get(cmd.id) for cmd in set_commands}
        # Check that actuators have the signals required
        [getattr(act_p, cmd.property) for act_p, cmd in zip([item for _, item in actuators.items()], set_commands)]

        await asyncio.gather(*[sig.connect() for sig in detectors + [item for _, item in actuators.items()]])
        # I now delegate it all down the road to the plan ...
        RE = self.mexec.run_engine
        RE(corrections_plan(
            oracle=self.oracle,
            policy=self.policy,
            # These are rather signals than detectors
            detectors=detectors,
            actuators=actuators,
            # todo: fix me layer violation
            info_signals=self.mexec.info_signals,
            md={},
            n_readings=self.num_readings
        ))
        raise NotImplementedError("Work to be done")
