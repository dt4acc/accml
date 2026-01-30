import logging

from accml.app.tune.model import TuneResponseCollection
from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml_lib.core.bl.command_rewritter import CommandRewriter
from accml_lib.core.model.output.tune import  Tune
from accml_lib.custom.bessyii.liasion_translator_setup import load_managers
from accml_lib.custom.bessyii.pyat_simulator_backend import simulator_backend

logging.basicConfig(level=logging.WARNING)

import yaml
import jsons

from accml.app.tune.tune_correction import tune_correction


async def main():
    with open("../03_reference_data/tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    yp, lm, ts = load_managers()

    mexec = BasicMeasurementExecutionEngine(
        backend=simulator_backend(filename="../03_reference_data/bessy2_storage_ring_reflat.json"),
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=SimpleDataStorage(),
        expected_view_for_output="device",
        num_readings=1
    )
    await tune_correction(dm, tune_target=Tune(x=1055, y=902), mexec=mexec)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
