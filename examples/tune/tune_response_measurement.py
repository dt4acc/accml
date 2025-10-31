import logging
logger = logging.basicConfig(level=logging.WARNING)

from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from databroker import catalog
from ophyd_async.core import soft_signal_rw

from accml.app.tune.tune_measurement import tune
from accml.core.model.identifiers import LatticeElementPropertyID
from accml.custom.bluesky.bluesky_measurement_execution_engine import BlueskyMeasurementExecutionEngine

from accml.custom.facility_specific.bessyii.liasion_translator_setup import load_managers
from accml.custom.facility_specific.bessyii.setup import setup
# from accml.custom.facility_specific.bessyii_on_tango.setup import setup


def main():
    """
    Todo:
        execution engine use and setup should be provided by standard measurement execution engine
        e.g. depending on Bluesky or Bliss what ever the lab's preference is
    """
    devices = setup()
    # Setup informational signals (mock metadata)
    info_sigs = {name: soft_signal_rw(str, name=name) for name in ["device_name", "channel_name"]}
    info_sigs["channel_value"] = soft_signal_rw(float, name= "channel_value", precision=5)


    # TODO: should be handled internally, but overridable
    lt = LiveTable([sig.name for _, sig in info_sigs.items()] +
                   ["tune-x-sig", "tune-y-sig"] +
                   ["tune-x", "tune-y"],
                   # + list(actuators.values())
                   default_prec=10, )
    RE = RunEngine()
    [RE.subscribe(consumer) for consumer in [lt]]
    # TODO: if you need to save the results, you need mongo and then uncomment the below two lines.
    db = catalog["heavy_local"]
    RE.subscribe(db.v1.insert)
    # TODO: need to address live plots
    #   here a databroker should be added so that data can be accessed
    #   later on

    yp, lm, _ = load_managers()
    # Todo: remove this line after only Q3/Q4 are flagged as tune correction magnets
    tune_correction_quads = [name for name in yp.tune_correction_quadrupole_names() if name[1] in ["3", "4"]]
    #  Find out to which power converters these are connected to
    pc_names = {
        lm.forward(LatticeElementPropertyID(name, "main_strength")).device_name:
            name for name in tune_correction_quads
    }
    # Now I add a hack: I only use quadrupoles whoes power converter is unique
    # I should rather work in device space right away
    pc_names=list(set(pc_names))
    tune(
       devices=devices,
       quadrupole_pc_names=pc_names,
       measurement_values=[0, 1e0, 0, -1e0, 0],
       mexec=BlueskyMeasurementExecutionEngine(run_engine=RE),
       info_signals=info_sigs
    )


if __name__ == "__main__":
    main()