import asyncio
import logging

from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml.custom.ophyd_async.ophyd_async_backend import OphydAsyncDeviceBackendRW
from accml.custom.ophyd_async.ophyd_async_measurement_execution_engine import OphydAsyncDeltaBackendRWProxy
from accml_lib.core.bl.command_rewritter import CommandRewriter
from accml_lib.core.bl.delta_backend import StateCache
from accml_lib.core.model.output.tune import Tune
from accml_lib.custom.bessyii.liasion_translator_setup import load_managers
from accml_lib.custom.bessyii.setup import setup

logging.basicConfig(level=logging.WARNING)

import yaml
import jsons

from accml.app.tune.model import  TuneResponseCollection
from accml.app.tune.tune_correction import tune_correction



def main():
    with open("../tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    yp, lm, ts = load_managers()
    devices = setup(prefix="")

    async def connect():
        await devices.get("tune").connect()
        await devices.get('quadrupole_pcs').connect()
        # await devices.g

    asyncio.get_event_loop().run_until_complete(connect())

    backend = OphydAsyncDeltaBackendRWProxy(
        OphydAsyncDeviceBackendRW(devices=devices),
        cache=StateCache(name="BESSY2_OphydAsync_Dev_State_Cache"),
    )
    mexec = BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=SimpleDataStorage(),
        expected_view_for_output="device"
    )
    tune_correction(dm, tune_target=Tune(x=1060, y=907), n_iterations=2, mexec=mexec)


if __name__ == "__main__":
    main()
