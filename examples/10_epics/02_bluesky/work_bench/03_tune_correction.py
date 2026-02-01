import logging
from pathlib import Path

import jsons
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from ophyd_async.core import soft_signal_rw
import yaml

logging.basicConfig(level=logging.WARNING)

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.lib_.custom.bessyii as b2

# Now here we have a name clash
from accml.app.tune.bluesky.tune_correction import tune_correction
# need to import it here ... it used below
import accml.work_bench.custom.bluesky

data_dir = Path(__name__).absolute().parent.parent.parent.parent


async def main():
    with open(data_dir / "05_reference_data" / "tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, wb.app.tune.TuneResponseCollection)

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
    mexec = wb.custom.bluesky.BlueskyMeasurementExecutionEngine(
        run_engine=RE,
        devices=b2.bessyii_setup(prefix=None),
        info_signals=info_sigs,
        cache=wba.StateCache(name="bluesky-based-tune-correction-reference"),
    )

    await tune_correction(dm, mexec=mexec, tune_target=wba.Tune(x=1055, y=902))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
