import logging

from accml.core.bl.delta_backend import DeltaBackendRWProxy, StateCache

logging.basicConfig(level=logging.WARNING)

import yaml
import jsons

from accml.app.tune.model import TuneResponseCollection
from accml.app.tune.tune_correction import tune_correction
from accml.core.bl.command_rewritter import CommandRewriter
from accml.core.simulator.simulator_execution_engine import SimpleDataStorage, SimulatorExecutionEngine
from accml.custom.accml_lib.bessyii.bessyii_pyat_lattice import bessyii_pyat_lattice
from accml.custom.accml_lib.bessyii.liasion_translator_setup import load_managers
from accml.custom.simulators.model.tune import Tune
from accml.custom.simulators.pyat.accelerator_simulator import PyATAcceleratorSimulator
from accml.custom.simulators.pyat.simulator_backend import SimulatorBackend


def main():
    with open("tune_result.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    acc = PyATAcceleratorSimulator(at_lattice=bessyii_pyat_lattice(filename="bessy2_storage_ring_reflat.json"))
    backend = DeltaBackendRWProxy(
        backend=SimulatorBackend(name="BESSY_on_PyAT", acc=acc),
        cache=StateCache(name="BESSY_on_PyAT_delta_state_cache")
    )
    storage = SimpleDataStorage()

    yp, lm, ts = load_managers()
    mexec = SimulatorExecutionEngine(
        backend=backend,
        cmd_rewritter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=storage
    )
    tune_correction(dm, tune_target=Tune(x=1055, y=902), mexec=mexec)


if __name__ == "__main__":
    main()