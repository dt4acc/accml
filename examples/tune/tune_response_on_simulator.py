import json


import jsons

from accml.app.tune.tune_measurement import measure_tune_response
from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml_lib.core.bl.command_rewritter import CommandRewriter
from accml_lib.core.model.command import ReadCommand
from accml_lib.core.model.identifiers import LatticeElementPropertyID
from accml_lib.core.model.result import register_serializers_to_json_fork
from accml_lib.custom.bessyii.liasion_translator_setup import load_managers
from accml_lib.custom.bessyii.pyat_simulator_backend import simulator_backend

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
    backend = simulator_backend()
    storage = SimpleDataStorage()
    mexec = BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=storage,
        expected_view_for_output="device"
    )
    uuid = measure_tune_response(
       detectors=[
           ReadCommand("tune", "transversal"),
       ],
       quadrupole_pc_names=pc_names,
       measurement_values=[0, 1e0, 0, -1e0, 0],
       mexec=mexec,
       info_signals=None
    )
    data = storage.get(uuid)
    data = jsons.dump(data, fork_inst=jsons_fork)

    with open("tune_response_data_from_simulator.json", "wt") as fp:
        json.dump(data, fp, indent=4)


if __name__  == "__main__":
    main()