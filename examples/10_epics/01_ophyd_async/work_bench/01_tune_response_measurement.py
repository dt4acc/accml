import logging
logging.basicConfig(level=logging.WARNING)

import json
import jsons

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.lib_.custom.bessyii as b2

# need to import it here ... it used below
import accml.work_bench.custom.ophyd_async


async def main():
    yp, lm, ts = b2.bessyii_load_managers()
    devices = b2.bessyii_setup(prefix=None)

    # Todo: remove this line after only Q3/Q4 are flagged as tune correction magnets
    tune_correction_quads = [name for name in yp.tune_correction_quadrupole_names() if name[1] in ["3", "4"]]
    #  Find out to which power converters these are connected to
    pc_names = {
        lm.forward(wba.LatticeElementPropertyID(name, "main_strength")).device_name:
            name for name in tune_correction_quads
    }
    # Now I add a hack: I only use quadrupoles whoes power converter is unique
    # I should rather work in device space right away
    pc_names=list(set(pc_names))
    # here for demo only do it for two magnets
    # pc_names = pc_names[:2]
    storage = wba.SimpleDataStorage()

    await devices.get("tune").connect()
    await devices.get('quadrupole_pcs').connect()

    backend = wb.custom.ophyd_async.OphydAsyncDeltaBackendRWProxy(
        wb.custom.ophyd_async.OphydAsyncDeviceBackendRW(devices=devices),
        cache=wba.StateCache(name="BESSY2_OphydAsync_Dev_State_Cache"),
    )
    mexec = wba.BasicMeasurementExecutionEngine(
        backend=backend,
        cmd_rewriter=wba.CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=storage,
        expected_view_for_output="device",
        num_readings=3
    )

    uuid = await wb.app.tune.measure_tune_response(
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
    data = jsons.dump(data)

    with open("../../04_measurement_simulation_data/tune_response_data_with_ophyd_async.json", "wt") as fp:
        json.dump(data, fp, indent=4)


if __name__  == "__main__":
    import asyncio
    asyncio.run(main())
