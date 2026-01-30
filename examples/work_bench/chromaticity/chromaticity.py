import asyncio
import json
import logging

import numpy as np

logging.basicConfig(level=logging.WARNING)

import jsons

# load the necessary sub module
import accml.work_bench.custom.ophyd_async

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.lib_.custom.bessyii as b2


async def main():
    n_steps = 3
    freq_factor = .5

    # from some previous scripts ... can be made better
    df = 730e-3 * 5  # *.8
    fstart = - 1.5 * freq_factor * df
    fend   = + 1.  * freq_factor * df

    frequencies = [0] + np.linspace(fstart, fend, n_steps).tolist()
    
    cmds_on_machine = []
    for val in frequencies:
        cmds_on_machine.append(
            wba.TransactionCommand(transaction=[
                    wba.Command(
                        id="mc-frequency",
                        property="delta_setpoint",
                        value=val,
                        behaviour_on_error=wba.BehaviourOnError.stop
                    )
            ])
        )
    cmds_on_machine = wba.CommandSequence(commands=cmds_on_machine)
    # pprint.pprint (cmds_on_machine)

    state_cache = wba.StateCache(name="chromaticity-measurement")
    state_cache.cache

    if False:
        backend = b2.bessyii_simulator_backend("bessy2_storage_ring_reflat.json")
        delta_backend = wba.DeltaBackendRWProxy(
            backend=backend,
            cache=state_cache
        )
    else:
        devices = b2.bessyii_setup(prefix=None)
        # the measurement execution engine can do this connection directly
        # at this stage I prefer to do it myself here.
        # When the connection fails later on it will be not so straight forward
        # to see what went wrong.
        # One can inspect the plans below to see which devices are called
        mc = devices.get("master_clock")
        assert mc, "No master clock defined"
        await mc.connect()
        tune_dev = devices.get("tune")
        assert tune_dev, "No tune device defined"
        await tune_dev.connect()
        del mc, tune_dev
        backend = wb.custom.ophyd_async.OphydAsyncDeviceBackendRW(devices=devices)
        delta_backend = wb.custom.ophyd_async.OphydAsyncDeltaBackendRWProxy(
            backend=backend,
            cache=state_cache
        )

    yp, lm, ts = b2.bessyii_load_managers()

    storage = wba.SimpleDataStorage()
    mexec = wba.BasicMeasurementExecutionEngine(
        backend=delta_backend,
        cmd_rewriter=wba.CommandRewriter(liaison_manager=lm, translation_service=ts),
        storage=storage,
        expected_view_for_output="device",
        num_readings=2
    )

    md = {}

    uid = await mexec.execute(
        detectors=[wba.ReadCommand(id="tune", property="transversal")],
        commands_collection=cmds_on_machine.commands,  # need to add bpms
        md=md,
        n_readings=2,
        wait_after_set=3,
        wait_between_sample=2,
        # delay=2
    )
    print(f"Chromaticity run created {uid=}")

    # One could make that a simple plan method
    # construct set back commands out of cache
    # for reliabitlity it should be handled by the calling processes
    rcmd = wba.ReadCommand(id="mc-frequency", property="setpoint")
    ref_value = state_cache.get(wba.ReadCommand(id="mc-frequency", property="setpoint"))
    if ref_value is None:
        known_keys = state_cache.keys()
    assert ref_value is not None, f"reference value for frequency is  none, but the following keys are known {known_keys}"
    print(f"{rcmd} started at {ref_value} .. setting it back")

    # This option does not work yet ... not to be able to configure
    # mexec to not store all values at startup
    # print("resetting to cached value: setting delta frequency to 0.0")

    # better don't get these values wrong ....
    cmd = [
        wba.TransactionCommand(
            transaction=[
                wba.Command(
                    id="mc-frequency",
                    property="setpoint",
                    value=ref_value["mc-frequency-setpoint"]["value"],
                    behaviour_on_error=wba.BehaviourOnError.stop
                )
            ]
        )
    ]

    uuid = await mexec.execute(
        detectors=[wba.ReadCommand(id="tune", property="transversal")],
        commands_collection=cmd,
        md=md,
        wait_after_set=3,
        wait_between_sample=2,
        n_readings=3
        # delay=2
    )

    data = storage.get(uuid)
    data = jsons.dump(data)

    with open("chromaticity_response_data_from_simulator.json", "wt") as fp:
        json.dump(data, fp, indent=4)

    return uid



if __name__ == "__main__":
    asyncio.run(main())
