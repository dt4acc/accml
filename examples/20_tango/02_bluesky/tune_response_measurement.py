"""Reading tune: adapted to soleil

There are many imports below here. At the current state the

"""
import asyncio
import logging
import pprint

logger = logging.basicConfig(level=logging.WARNING)

from accml.custom.bluesky.bluesky_measurement_execution_engine import (
    BlueskyMeasurementExecutionEngine,
)

from accml_lib.core.bl.delta_backend import StateCache
from accml_lib.core.model.utils.command import ReadCommand, TransactionCommand, Command, BehaviourOnError
from accml_lib.custom.soleil.manager_setup import load_managers
from accml_lib.custom.soleil.setup import setup

from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from databroker import catalog
from ophyd_async.core import soft_signal_rw


async def main():
    """
    Todo:
        execution engine use and setup should be provided by standard measurement execution engine
        e.g. depending on Bluesky or Bliss what ever the lab's preference is
    """
    # Setup informational signals (mock metadata)

    yp, _, __ = load_managers()
    tune_correction_quads = yp.get("tune_correction_quadrupoles")
    tune_name, = yp.get("tune")


    devices = setup()
    # not strictly necessary here ... but I rather like to check
    # that I have connection to devices. Bluesky Run engine will
    # create a much longer back trace
    for trl in tune_correction_quads+ ["tune"]:
        dev = devices.get(trl)
        assert dev is not None, f"Failed to get device for {trl}"
        await dev.connect()

    tune = devices.get("tune")
    # I needed to find out how the tune is named here
    # the keys I then added to the signals I want to see on the life table
    # pprint.pprint(await tune.describe())

    detectors=[ReadCommand(id="tune", property="transversal")]
    measurement_values=[0, 1e-4, 0, -1e-4, 0]

    info_sigs = {
        name: soft_signal_rw(str, name=name) for name in ["device_name", "channel_name"]
    }
    info_sigs["channel_value"] = soft_signal_rw(
        float, name="channel_value", precision=4
    )

    # TODO: should be handled internally, but overridable
    lt = LiveTable(
        [sig.name for _, sig in info_sigs.items()] +
        ["tune-Tune_h", "tune-Tune_v"],
        # required so that the TRL of the magnet is visible
        min_width=21
    )
    RE = RunEngine()
    [RE.subscribe(consumer) for consumer in [lt]]
    # TODO: if you need to save the results, you need mongo and then uncomment the below two lines.
    db = catalog["heavy_local"]
    RE.subscribe(db.v1.insert)

    mexec=BlueskyMeasurementExecutionEngine(
        run_engine=RE,
        devices=devices,
        info_signals=info_sigs,
        cache=StateCache(name="reference-data-cache-used-by-bluesky"),
    )

    cmds_on_machine = []
    for name in tune_correction_quads:
        for val in measurement_values:
            cmds_on_machine.append(
                TransactionCommand(
                    transaction=[
                        Command(id=name, property="delta_Strength", value=val, behaviour_on_error=BehaviourOnError.stop)
                    ]
                )
            )
    md = {}

    uid = await mexec.execute(
        detectors=detectors,
        commands_collection=cmds_on_machine,
        n_readings=3,
        md=md,
        retrieve_reference=True
    )

    print(f"Measurement {uid=}")


if __name__ == "__main__":
    asyncio.run(main())
