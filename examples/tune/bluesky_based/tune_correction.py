import logging

from accml.app.tune.tune_correction_bluesky import tune_correction

logger = logging.basicConfig(level=logging.WARNING)

import jsons
import yaml
from accml.app.tune.model import TuneResponseCollection, Tune

from accml.custom.bluesky.bluesky_measurement_execution_engine import (
    BlueskyMeasurementExecutionEngine,
)
from accml.custom.accml_lib.bessyii.setup import setup

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

    lt = LiveTable(
        ["tune-x-sig", "tune-y-sig"]
        + ["tune-x", "tune-y"]
        + [sig.name for _, sig in info_sigs.items()],
        default_prec=10,
    )
    RE = RunEngine()
    RE.subscribe(lt)
    mexec = BlueskyMeasurementExecutionEngine(
        run_engine=RE,
        devices=setup(),
        info_signals=info_sigs
    )

    tune_correction(dm, mexec=mexec, tune_target=Tune(x=1055, y=902))


if __name__ == "__main__":
    main()
