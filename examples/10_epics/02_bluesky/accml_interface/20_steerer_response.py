"""
Warning:
    Steerers currently not exported in BESSY II twin.
"""
import asyncio
import logging
logging.basicConfig(level=logging.WARNING)


from accml_lib.core.bl.delta_backend import StateCache
from accml.custom.bluesky.bluesky_measurement_execution_engine import (
    BlueskyMeasurementExecutionEngine,
)

from accml_lib.core.model.utils.command import Command, ReadCommand, TransactionCommand, BehaviourOnError, CommandSequence
from accml_lib.custom.bessyii.setup import setup


from ophyd_async.core import soft_signal_rw
from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from databroker import catalog

import pprint

async def main():

    devices = setup(prefix=None)
    orbit = devices.get("orbit")
    assert orbit is not None, "Could not load orbit"
    steerer_pcs = devices.get("steerer_pcs")
    assert steerer_pcs is not None, "Could not load steerer pcs"
    await asyncio.gather(*([orbit.connect()] + [pc.connect() for _, pc in steerer_pcs.items()]))
    await orbit.describe()
    # pprint.pprint(await orbit.read())
    measurement_values = [0, -0.1, 0, +0.1, 0]

    cmds_on_machine = []
    for name in steerer_pcs:
        for val in measurement_values:
            cmds_on_machine.append(
                TransactionCommand(
                    transaction=[Command(id=name, property="delta_set_current", value=val, behaviour_on_error=BehaviourOnError.stop)]
                )
            )


    # Setup informational signals (mock metadata)
    info_sigs = {
        name: soft_signal_rw(str, name=name) for name in ["device_name", "channel_name"]
    }
    info_sigs["channel_value"] = soft_signal_rw(
        float, name="channel_value", precision=5
    )

    # TODO: should be handled internally, but overridable
    lt = LiveTable(
        [sig.name for _, sig in info_sigs.items()],
        # + list(actuators.values())
        default_prec=10,
    )
    # db = catalog["heavy_local"]
    RE = RunEngine()
    [RE.subscribe(consumer) for consumer in [lt]]    
    # RE.subscribe(db.v1.insert)

    state_cache = StateCache(name="chromaticity-measurement")
    state_cache.cache
    mexec = BlueskyMeasurementExecutionEngine(
        run_engine=RE,
        devices=setup(prefix=""),
        info_signals=info_sigs,
        cache=state_cache
    )

    md = {}
    uid = await mexec.execute(
        detectors=[ReadCommand(id="orbit", property="pos")],
        commands_collection=cmds_on_machine,  # need to add bpms
        md=md,
        wait_after_set=.5,
        wait_between_sample=.2,
        n_readings=3

    )
    print(f"Run created {uid=}")
    # whzy do I get so many errors at the end
    await asyncio.sleep(5)
    return uid


if __name__ == "__main__":
    asyncio.run(main())
