import asyncio
import json
import logging

import numpy as np

logging.basicConfig(level=logging.WARNING)

import jsons

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

    backend = b2.bessyii_simulator_backend("bessy2_storage_ring_reflat.json")
    delta_backend = wba.Delta
    mexec = wba.BasicMeasurementExecutionEngine(
        cache=state_cache
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
    assert ref_value is not None, "reference value is none"
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
                    value=ref_value,
                    behaviour_on_error=wba.BehaviourOnError.stop
                )
            ]
        )
    ]

    uid = await mexec.execute(
        detectors=[wba.ReadCommand(id="tune", property="transversal")],
        commands_collection=cmd,
        md=md,
        wait_after_set=3,
        wait_between_sample=2,
        n_readings=3
        # delay=2
    )

    return uid



if __name__ == "__main__":
    asyncio.run(main())
