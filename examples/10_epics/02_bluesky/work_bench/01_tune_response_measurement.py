import logging
logging.basicConfig(level=logging.WARNING)

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.lib_.custom.bessyii as b2

# need to import it here ... it used below
import accml.work_bench.custom.bluesky

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
    info_sigs = {
        name: soft_signal_rw(str, name=name) for name in ["device_name", "channel_name"]
    }
    info_sigs["channel_value"] = soft_signal_rw(
        float, name="channel_value", precision=5
    )

    # TODO: should be handled internally, but overridable
    lt = LiveTable(
        [sig.name for _, sig in info_sigs.items()]
        + ["tune-transversal-x-sig", "tune-transversal-y-sig"]
        + ["tune-x", "tune-y"],
        # + list(actuators.values())
        default_prec=10,
    )
    RE = RunEngine()
    [RE.subscribe(consumer) for consumer in [lt]]
    # TODO: if you need to save the results, you need mongo and then uncomment the below two lines.
    # db = catalog["heavy_local"]
    # RE.subscribe(db.v1.insert)

    yp, lm, _ = b2.bessyii_load_managers()
    # Todo: remove this line after only Q3/Q4 are flagged as tune correction magnets
    tune_correction_quads = [
        name for name in yp.tune_correction_quadrupole_names() if name[1] in ["3", "4"]
    ]
    #  Find out to which power converters these are connected to
    pc_names = {
        lm.forward(wba.LatticeElementPropertyID(name, "main_strength")).device_name: name
        for name in tune_correction_quads
    }
    # Now I add a hack: I only use quadrupoles whoes power converter is unique
    # I should rather work in device space right away
    pc_names = list(set(pc_names))
    uid = await wb.app.tune.measure_tune_response(
        detectors=[wba.ReadCommand(id="tune", property="transversal")],
        quadrupole_pc_names=pc_names,
        measurement_values=[0, 1e0, 0, -1e0, 0],
        mexec=wb.custom.bluesky.BlueskyMeasurementExecutionEngine(
            run_engine=RE,
            devices=b2.bessyii_setup(prefix=None),
            info_signals=info_sigs,
            cache=wba.StateCache(name="reference-data-cache-used-by-bluesky"),
        ),
        n_readings=3,
        retrieve_reference=True
    )
    print(f"Measurement {uid=}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
