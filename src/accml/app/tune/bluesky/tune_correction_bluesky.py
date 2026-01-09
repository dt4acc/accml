import asyncio
import logging

from .bluesky_tune_correction_controller import BlueskyTuneCorrectionController
from .model import TuneResponseCollection
from .oracle import TuneOracle
from .policy import TunePolicy
from .tune_correction_controller import TuneCorrectionController
from ...core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from ...core.model.command import ReadCommand
from ...custom.simulators.interface.calculation_output import Tune

logger = logging.getLogger("accml")


def tune_correction(
    dm: TuneResponseCollection,
    tune_target: Tune,
    mexec: MeasurementExecutionEngine,
    **kwargs
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
    controller = BlueskyTuneCorrectionController(
        oracle=oracle,
        policy=policy,
        mexec=mexec,
        num_readings=2,
        wait_before_read=0.1,
        delay=0.1,
    )

    rcmds = [ReadCommand(id="tune", property="transversal")]
    set_cmds = [ReadCommand(id=elm.pc_name, property="delta_set_current") for elm in dm.col]

    async def run_continously():
        await controller.continuous(read_commands=rcmds, set_commands=set_cmds)

    asyncio.get_event_loop().run_until_complete(run_continously())
