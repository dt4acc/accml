from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from databroker import catalog
from ophyd import Signal

from accml.app.tune.tune_measurement import tune
from accml.core.bl.liasion_translator_setup import load_managers
from accml.core.model.identifiers import LatticeElementPropertyID
# from accml.custom.epics.bluesky_measurement_execution_engine import BlueskyMeasurementExecutionEngine
from accml.custom.tango.mexec.measurement_execution_engine import AsyncMeasurementExecutionEngine


# Todo: execution engine use and setup should be provided by standard measurement execution engine
#       e.g. depending on Bluesky or Bliss what ever the lab's preference is
#


if __name__ == "__main__":
    # TODO: use the generic (not bluesky dependent) mesaurement execution engine


    info_sigs = {name: Signal(name=name) for name in ["device_name", "channel_name", "channel_value"]}
    # TODO: should be handled internally, but overridable
    lt = LiveTable([sig.name for _, sig in info_sigs.items()] + ["tune-x-sig", "tune-y-sig"],
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
       quadrupole_pc_names=pc_names,
       measurement_values=[0, 1e0, 0, -1e0, 0],
       mexec=AsyncMeasurementExecutionEngine(run_engine=RE),
       info_signals=info_sigs
    )