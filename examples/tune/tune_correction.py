import logging

logger = logging.basicConfig(level=logging.WARNING)

import jsons
import yaml
from accml.app.tune.model import TuneResponseCollection
from accml.app.tune.tune_correction import tune_correction
from accml.custom.bluesky.bluesky_measurement_execution_engine import (
    BlueskyMeasurementExecutionEngine,
)
from accml.custom.facility_specific.bessyii.setup import setup

from ophyd_async.core import soft_signal_rw
from bluesky import RunEngine
from bluesky.callbacks import LiveTable


def main():
    with open("tune_result.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    sig_names = (
        ["tune-x-delta", "tune-y-delta"]
        + [f"applied-{st}" for st in ["mean", "std", "min", "max"]]
        + [f"oracle-{st}" for st in ["mean", "std", "min", "max"]]
    )

    info_sigs = {
        name: soft_signal_rw(float, name=name, precision=8) for name in sig_names
    }

    devices = setup()
    lt = LiveTable(
        ["tune-x-sig", "tune-y-sig"]
        + ["tune-x", "tune-y"]
        + [sig.name for _, sig in info_sigs.items()],
        default_prec=10,
    )
    RE = RunEngine()
    RE.subscribe(lt)
    mexec = BlueskyMeasurementExecutionEngine(run_engine=RE)

    tune_correction(dm, devices=devices, mexec=mexec, info_signals=info_sigs)


if __name__ == "__main__":
    main()
