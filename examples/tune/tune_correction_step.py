"""

Todo:
    as this is a demonstration of a correction loop
    Should one still run bluesky on it

    I am implementing it based on bluesky ... one can then see later
"""

import jsons
import yaml
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from ophyd import Signal

from accml.app.tune.model import TuneResponseForFit
from accml.app.tune.model_io import install_jsons_io
from accml.app.tune.tune_correction_oracle import TuneCorrectionOracle
from accml.app.tune.tune_correction_step import tune_correction_step
from accml.custom.epics.mexec.bluesky.bluesky_measurement_execution_engine import BlueskyMeasurementExecutionEngine

install_jsons_io()


def main():
    with open("tune_oracle_data.yml") as fp:
        d = yaml.safe_load(fp)
    data_for_fit = jsons.load(d, TuneResponseForFit)
    oracle = TuneCorrectionOracle(data_for_fit)

    RE = RunEngine()
    info_sigs = {name: Signal(name=name) for name in ["device_name", "channel_name", "channel_value"]}
    # TODO: should be handled internally, but overridable
    lt = LiveTable([sig.name for _, sig in info_sigs.items()] + ["tune-x-sig", "tune-y-sig"],
                   # + list(actuators.values())
                   default_prec=10, )
    RE = RunEngine()
    [RE.subscribe(consumer) for consumer in [lt]]

    mexec = BlueskyMeasurementExecutionEngine(run_engine=RE)
    tune_correction_step(
        mexec=mexec,
        oracle=oracle,
        data_keys=["tune-x-sig", "tune-y-sig"],
        targets=[0.848070153, 0.870114641],
        quadrupole_pc_names=[],
        info_signals=info_sigs,
        repeat_readings=3
    )

if __name__ == "__main__":
    main()