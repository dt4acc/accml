import logging

from accml_lib.core.bl.delta_backend import StateCache

logging.basicConfig(level=logging.WARNING)

import jsons
import yaml
from accml.app.tune.model import TuneResponseCollection
from accml.app.tune.bluesky.tune_correction import tune_correction
from accml.custom.bluesky.bluesky_measurement_execution_engine import (
    BlueskyMeasurementExecutionEngine,
)
from accml_lib.core.model.tune import Tune
from accml_lib.custom.bessyii.setup import setup


from ophyd_async.core import soft_signal_rw
from bluesky import RunEngine
from bluesky.callbacks import LiveTable


def main():
    with open("../tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    sig_names = ["tune-x-delta", "tune-y-delta"] + [
        f"applied-{st}" for st in ["mean", "std", "min", "max"]
    ]

    info_sigs = {
        name: soft_signal_rw(float, name=name, precision=8) for name in sig_names
    }

    lt = LiveTable(
        ["tune-transversal-x-sig", "tune-transversal-y-sig"]
        + [sig.name for _, sig in info_sigs.items()],
        default_prec=10,
    )
    RE = RunEngine()
    RE.subscribe(lt)
    mexec = BlueskyMeasurementExecutionEngine(
        run_engine=RE, devices=setup(), info_signals=info_sigs, cache=StateCache(name="bluesky-based-tune-coeewxrion"),
    )

    tune_correction(dm, mexec=mexec, tune_target=Tune(x=1055, y=902))


if __name__ == "__main__":
    main()
