import logging

import numpy as np

logging.basicConfig(level=logging.WARNING)

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.lib_.custom.bessyii as b2
import accml.work_bench.custom.bluesky

from ophyd_async.core import soft_signal_rw
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from databroker import catalog

import pprint

async def main():
    test = False
    video = True
    if test:
        n_steps = 3
        freq_factor = 0.1
    elif video:
        n_steps = 3
        freq_factor = .5
    else:
        n_steps = 5
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

    info_sigs = {
        name: soft_signal_rw(str, name=name) for name in ["device_name", "channel_name"]
    }
    info_sigs["channel_value"] = soft_signal_rw(
        float, name="channel_value", precision=10
    )


    # Todo: need to keeps these names
    lt = LiveTable(
        # Todo: a lifetable that can handle read commands and set commands ...
        ["mc-frequency-setpoint"] +
        ["tune-transversal-x-sig", "tune-transversal-y-sig"]
        + [sig.name for _, sig in info_sigs.items()],
        default_prec=10,
    )


    RE = RunEngine()
    RE.subscribe(lt)
    # db = catalog["heavy"]
    # RE.subscribe(db.v1.insert)
    state_cache = wba.StateCache(name="chromaticity-measurement")
    state_cache.cache
    mexec = wb.custom.bluesky.BlueskyMeasurementExecutionEngine(
        run_engine=RE,
        devices=b2.bessyii_setup(prefix=None),
        info_signals=info_sigs,
        cache=state_cache
    )

    md = {}

    uid = await mexec.execute(
        detectors=[wba.ReadCommand(id="tune", property="transversal")],
        commands_collection=cmds_on_machine.commands,  # need to add bpms
        md=md,
        retrieve_reference=True,
        n_readings=2,
        wait_after_set=3,
        wait_between_samples=2,
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
        retrieve_reference=True,
        wait_after_set=3,
        wait_between_samples=2,
        n_readings=3,
        # delay=2
    )

    return uid



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
