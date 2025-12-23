import json


import jsons

from accml.app.tune.tune_measurement import tune
from accml.core.bl.command_rewritter import CommandRewriter
from accml.core.model.command import Command, ReadCommand
from accml.core.model.identifiers import LatticeElementPropertyID
from accml.core.model.result import register_serializers_to_json_fork
from accml.core.simulator.simulator_execution_engine import SimulatorExecutionEngine, SimpleDataStorage
from accml.custom.accml_lib.bessyii.bessyii_pyat_lattice import bessyii_pyat_lattice
from accml.custom.accml_lib.bessyii.liasion_translator_setup import load_managers
from accml.custom.simulators.pyat.accelerator_simulator import PyATAcceleratorSimulator
from accml.custom.simulators.pyat.simulator_backend import SimulatorBackend

jsons_fork = jsons.fork()
register_serializers_to_json_fork(jsons_fork)


def main():
    yp, lm, ts = load_managers()
    # Todo: remove this line after only Q3/Q4 are flagged as tune correction magnets
    tune_correction_quads = [name for name in yp.tune_correction_quadrupole_names() if name[1] in ["3", "4"]]
    #  Find out to which power converters these are connected to
    pc_names = {
        lm.forward(LatticeElementPropertyID(name, "main_strength")).device_name:
            name for name in tune_correction_quads
    }
    # Now I add a hack: I only use quadrupoles whoes power converter is unique
    # I should rather work in device space right away
    pc_names=list(set(pc_names))

    acc = PyATAcceleratorSimulator(at_lattice=bessyii_pyat_lattice(filename="bessy2_storage_ring_reflat.json"))
    backend = SimulatorBackend(name="BESSY_on_PyAT", acc=acc)
    storage = SimpleDataStorage()
    mexec = SimulatorExecutionEngine(
        backend=backend,
        cmd_rewritter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=storage
    )
    uuid = tune(
       devices=[
           ReadCommand("tune", "transversal"),
       ],
       quadrupole_pc_names=pc_names,
       measurement_values=[0, 1e0, 0, -1e0, 0],
       mexec=mexec,
       info_signals=None
    )
    data = storage.get(uuid)
    data = jsons.dump(data, fork_inst=jsons_fork)

    with open("data_storage.json", "wt") as fp:
        json.dump(data, fp, indent=4)


if __name__  == "__main__":
    main()