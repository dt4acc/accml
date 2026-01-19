import asyncio
import logging

from accml_lib.core.interfaces.utils.measurement_execution_engine import MeasurementExecutionEngine
from accml_lib.core.interfaces.simulator.calculation_output import Tune
from accml_lib.core.model.utils.command import ReadCommand
from .tune_correction_controller import BlueskyTuneCorrectionController
from ..model import TuneResponseCollection
from ..oracle import TuneOracle
from ..policy import TunePolicy


logger = logging.getLogger("accml")


def tune_correction(
    dm: TuneResponseCollection,
    tune_target: Tune,
    mexec: MeasurementExecutionEngine,
    n_iterations=3,
    n_samples=2,
    wait_after_set=0.5,
    wait_between_sample=0.1,
    **kwargs
):
    oracle = TuneOracle(col=dm, target=tune_target)
    policy = TunePolicy(scale=1.0)
    logger.info("correction start")
    controller = BlueskyTuneCorrectionController(
        oracle=oracle,
        policy=policy,
        mexec=mexec,
        num_readings=n_samples,
        wait_before_read=wait_after_set,
        delay=wait_between_sample,
    )

    rcmds = [ReadCommand(id="tune", property="transversal")]
    set_cmds = [
        ReadCommand(id=elm.pc_name, property="delta_set_current") for elm in dm.col
    ]

    async def run_continuously():
        await controller.continuous(read_commands=rcmds, set_commands=set_cmds, n_steps=n_iterations)

    asyncio.get_event_loop().run_until_complete(run_continuously())
