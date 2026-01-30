import logging
logging.basicConfig(level=logging.WARNING)

import asyncio
import yaml
import jsons

from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml.custom.ophyd_async.ophyd_async_backend import OphydAsyncDeviceBackendRW
from accml.custom.ophyd_async.ophyd_async_delta_backend import OphydAsyncDeltaBackendRWProxy
from accml_lib.core.bl.command_rewritter import CommandRewriter
from accml_lib.core.bl.delta_backend import StateCache
from accml_lib.core.model.output.tune import Tune
from accml_lib.custom.bessyii.liasion_translator_setup import load_managers
from accml_lib.custom.bessyii.setup import setup
from accml.app.tune.model import  TuneResponseCollection
from accml.app.tune.tune_correction import tune_correction


async def main():
    with open("../../03_reference_data/tune_response_from_simulation.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)
    dm = jsons.load(d, TuneResponseCollection)

    yp, lm, ts = load_managers()
    # ON BESSY II machine
    # devices = setup(prefix="")
    # On Twin None ... means default
    devices = setup(prefix=None)

    await devices.get("tune").connect()
    await devices.get('quadrupole_pcs').connect()

    backend = OphydAsyncDeltaBackendRWProxy(
        OphydAsyncDeviceBackendRW(devices=devices),
        cache=StateCache(name="BESSY2_OphydAsync_Dev_State_Cache"),
    )
    mexec = BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=SimpleDataStorage(),
        expected_view_for_output="device",
        num_readings=1
    )
    await tune_correction(dm, tune_target=Tune(x=1055, y=902), n_iterations=2, mexec=mexec)


if __name__ == "__main__":
    asyncio.run(main())
