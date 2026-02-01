import asyncio
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING)

import jsons

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.lib_.custom.bessyii as b2

data_dir = Path(__name__).absolute().parent.parent.parent


async def main():
    yp, lm, ts = b2.bessyii_load_managers()
    # Todo: remove this line after only Q3/Q4 are flagged as tune correction magnets
    tune_correction_quads = [name for name in yp.tune_correction_quadrupole_names() if name[1] in ["3", "4"]]
    #  Find out to which power converters these are connected to
    pc_names = {
        lm.forward(wba.LatticeElementPropertyID(name, "main_strength")).device_name:
            name for name in tune_correction_quads
    }
    # Now I add a hack: I only use quadrupoles whoes power converter is unique
    # I should rather work in device space right away
    pc_names=list(set(pc_names))
    backend = b2.bessyii_simulator_backend(data_dir / "05_reference_data" / "bessy2_storage_ring_reflat.json")
    storage = wba.SimpleDataStorage()
    mexec = wba.BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=wba.CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=storage,
        expected_view_for_output="device",
        num_readings=1,
    )
    uuid = await wb.app.tune.measure_tune_response(
       detectors=[
           wba.ReadCommand("tune", "transversal"),
       ],
       quadrupole_pc_names=pc_names,
       measurement_values=[0, 1e0, 0, -1e0, 0],
       mexec=mexec,
       info_signals=None
    )
    data = storage.get(uuid)
    data = jsons.dump(data)

    with open(data_dir / "06_measurement_simulation_data" / "tune_response_data_from_simulator.json", "wt") as fp:
        json.dump(data, fp, indent=4)


if __name__  == "__main__":
    asyncio.run(main())