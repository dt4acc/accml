import logging
logging.basicConfig(level=logging.WARNING)

import json
import jsons
from pathlib import Path
import yaml

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.lib_.custom.bessyii as b2

# need to import it here ... it used below
import accml.work_bench.custom.ophyd_async

data_dir = Path(__name__).absolute().parent.parent.parent.parent


async def main():
    with open(data_dir /"05_reference_data" / "tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, wb.app.tune.TuneResponseCollection)

    yp, lm, ts = b2.bessyii_load_managers()
    # ON BESSY II machine
    # devices = setup(prefix="")
    # On Twin None ... means default
    devices = b2.bessyii_setup(prefix=None)

    await devices.get("tune").connect()
    await devices.get('quadrupole_pcs').connect()

    backend = wb.custom.ophyd_async.OphydAsyncDeltaBackendRWProxy(
        wb.custom.ophyd_async.OphydAsyncDeviceBackendRW(devices=devices),
        cache=wba.StateCache(name="BESSY2_OphydAsync_Dev_State_Cache"),
    )
    mexec = wba.BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=wba.CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=wba.SimpleDataStorage(),
        expected_view_for_output="device",
        num_readings=1
    )
    await wb.app.tune.tune_correction(dm, tune_target=wba.Tune(x=1060, y=907), n_iterations=2, mexec=mexec)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
