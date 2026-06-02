import logging

from dt4acc.custom_facility.als.liaison_translator_setup import load_managers
from dt4acc.custom_facility.als.ophyd_async_devices_setup import setup

# if not given aioca will provide a lot of output
logging.basicConfig(level=logging.WARNING)

import json
import jsons

from accml.app.tune.tune_measurement import measure_tune_response
from accml.core.utils.basic_measurement_execution_engine import BasicMeasurementExecutionEngine
from accml.core.utils.simple_storage import SimpleDataStorage
from accml.custom.ophyd_async.ophyd_async_backend import OphydAsyncDeviceBackendRW
from accml.custom.ophyd_async.ophyd_async_delta_backend import OphydAsyncDeltaBackendRWProxy
from accml_lib.core.bl.delta_backend import StateCache
from accml_lib.core.model import jsons_support
from dt4acc_lib.bl.command_rewritter import CommandRewriter
from dt4acc_lib.model.utils.identifiers import LatticeElementPropertyID
from dt4acc_lib.model.utils.command import ReadCommand



jsons_fork = jsons.fork()
jsons_support.register_serializers(jsons_fork)

async def main():
    yp, lm, ts, _ = load_managers()
    devices = setup(prefix=None)

    tune_correction_quads = yp.get("tune_correction_quadrupoles")
    #  Find out to which power converters these are connected to
    pc_names = {
        lm.forward(LatticeElementPropertyID(name, "main_strength")).device_name:
            name for name in tune_correction_quads
    }
    # Now I add a hack: I only use quadrupoles whoes power converter is unique
    # I should rather work in device space right away
    pc_names=list(set(pc_names))
    # here for demo only do it for two magnets
    pc_names = pc_names[:2]
    storage = SimpleDataStorage()

    await devices.get("tune").connect()
    await devices.get('quadrupole_pcs').connect()

    backend = OphydAsyncDeltaBackendRWProxy(
        backend=OphydAsyncDeviceBackendRW(devices=devices),
        cache=StateCache(name="BESSY2_OphydAsync_Dev_State_Cache"),
    )
    mexec = BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=storage,
        expected_view_for_output="device",
        num_readings=3
    )

    uuid = await measure_tune_response(
       detectors=[
           ReadCommand("tune", "transversal"),
       ],
       quadrupole_pc_names=pc_names,
       measurement_values=[0, 1e0, 0, -1e0, 0],
       mexec=mexec,
       info_signals=None,
        #
        n_sample=2
    )
    data = storage.get(uuid)
    data = jsons.dump(data, fork_inst=jsons_fork)

    with open("../../../06_measurement_simulation_data/tune_response_data_with_ophyd_async.json", "wt") as fp:
        json.dump(data, fp, indent=4)


if __name__  == "__main__":
    import asyncio
    asyncio.run(main())
