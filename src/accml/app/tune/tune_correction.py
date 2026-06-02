import asyncio
import logging

from accml_lib.core.interfaces.utils.measurement_execution_engine import MeasurementExecutionEngine
from accml_lib.core.model.output.tune import  Tune
from dt4acc_lib.model.utils.command import ReadCommand
from .model import TuneResponseCollection
from .oracle import TuneOracle
from .policy import TunePolicy
from .tune_correction_controller import TuneCorrectionController

logger = logging.getLogger("accml")


async def tune_correction(
    dm: TuneResponseCollection,
    tune_target: Tune,
    *,
    token_for_tune_data: str,
    n_iterations=3,
    n_samples=2,
    wait_after_set=0.5,
    wait_between_sample=0.1,
    mexec: MeasurementExecutionEngine,
):
    """

    Todo:

      * reference / target tune from caller
      * consider to provide fine tuning from the outside
      * only connect to the actuators actually required

    """

    oracle = TuneOracle(col=dm, target=tune_target)
    policy = TunePolicy(scale=1.0)
    logger.info("correction start")
    controller = TuneCorrectionController(
        oracle=oracle,
        policy=policy,
        mexec=mexec,
        n_samples=n_samples,
        wait_after_set=wait_after_set,
        wait_between_samples=wait_between_sample,
        token_for_tune_data=token_for_tune_data,
    )

    rcmds = [ReadCommand(id="tune", property="transversal")]
    set_cmds = [
        ReadCommand(id=elm.pc_name, property="delta_set_current") for elm in dm.col
    ]

    await controller.continuous(read_commands=rcmds, set_commands=set_cmds, n_steps=n_iterations)