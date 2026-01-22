import logging
logging.basicConfig(level=logging.WARNING)

import yaml
import jsons

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.lib.custom.bessyii as b2

def main():
    with open("tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, wb.app.tune.TuneResponseCollection)

    yp, lm, ts = b2.bessyii_load_managers()

    mexec = wba.BasicMeasurementExecutionEngine(
        backend=b2.bessyii_simulator_backend(filename="bessy2_storage_ring_reflat.json"),
        cmd_rewriter=wba.CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=wba.SimpleDataStorage(),
        expected_view_for_output="device",
    )
    wb.app.tune.tune_correction(dm, tune_target=wb.app.tune.Tune(x=1055, y=902), mexec=mexec)


if __name__ == "__main__":
    main()
