import logging
logging.basicConfig(level=logging.WARNING)

import asyncio
import yaml
import jsons

from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml.custom.ophyd_async.ophyd_async_backend import OphydAsyncDeviceBackendRW
from accml.custom.ophyd_async.ophyd_async_delta_backend import OphydAsyncDeltaBackendRWProxy
from accml_lib.core.bl.delta_backend import StateCache
from accml.app.tune.model import  TuneResponseCollection
from accml.app.tune.tune_correction import tune_correction
from dt4acc.custom_facility.als.liaison_translator_setup import load_managers
from dt4acc.custom_facility.als.ophyd_async_devices_setup import setup
from dt4acc_lib.bl.command_rewritter import CommandRewriter
from dt4acc_lib.model.output.tune import Tune


async def main():
    with open("../../../05_reference_data/tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    yp, lm, ts, epics_vars = load_managers()
    # ON BESSY II machine
    # devices = setup(prefix="")
    # On Twin None ... means default
    devices = setup(prefix=None)

    await devices.get("tune").connect()
    await devices.get('quadrupole_pcs').connect()

    backend = OphydAsyncDeltaBackendRWProxy(
        backend=OphydAsyncDeviceBackendRW(devices=devices),
        cache=StateCache(name="BESSY2_OphydAsync_Dev_State_Cache"),
    )
    mexec = BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=SimpleDataStorage(),
        expected_view_for_output="device",
        num_readings=1
    )
    await tune_correction(
        dm,
        tune_target=Tune(x=270, y=380),
        n_iterations=3,
        mexec=mexec,
        token_for_tune_data="tune-transversal",
    )


if __name__ == "__main__":
    asyncio.run(main())
