import logging

from accml.app.tune.model import TuneResponseCollection
from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml_lib.core.bl.delta_backend import StateCache
from accml_lib.custom.als.pyat_simulator_backend import simulator_backend
from dt4acc_lib.bl.command_rewritter import CommandRewriter
from dt4acc.custom_facility.als.liaison_translator_setup import load_managers
from dt4acc_lib.model.output.tune import Tune

# from accml_lib.core.model.output.tune import  Tune

logging.basicConfig(level=logging.WARNING)

import yaml
import jsons

from accml.app.tune.tune_correction import tune_correction


async def main():
    with open("../../05_reference_data/tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    reference_state_cache = StateCache(name="ALS_on_PyAT_delta_state_cache")
    backend = simulator_backend(reference_state_cache)

    yp, lm, ts, _ = load_managers()

    mexec = BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        expected_view_for_output="device",
        num_readings=1,
        storage=None
    )

    await tune_correction(dm, tune_target=Tune(x=1055, y=902), mexec=mexec)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
