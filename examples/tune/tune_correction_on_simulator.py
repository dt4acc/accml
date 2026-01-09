import logging

logging.basicConfig(level=logging.WARNING)

import yaml
import jsons

from accml.app.tune.model import TuneResponseCollection, Tune
from accml.app.tune.tune_correction import tune_correction
from accml.core.bl.command_rewritter import CommandRewriter
from accml.core.simulator.simulator_execution_engine import (
    SimpleDataStorage,
    SimulatorExecutionEngine,
)
from accml.custom.accml_lib.bessyii.liasion_translator_setup import load_managers
from accml.custom.accml_lib.bessyii.pyat_simulator_backend import simulator_backend


def main():
    with open("tune_response_from_twin.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    yp, lm, ts = load_managers()

    mexec = SimulatorExecutionEngine(
        backend=simulator_backend(),
        cmd_rewritter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=SimpleDataStorage(),
    )
    tune_correction(dm, tune_target=Tune(x=1055, y=902), mexec=mexec)


if __name__ == "__main__":
    main()
