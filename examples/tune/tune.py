from bluesky import RunEngine
from bluesky.callbacks import LiveTable
from databroker import catalog
from ophyd import Signal

from accml.app.tune.tune_measurement import tune
from accml.core.bl.liasion_translator_setup import load_managers
from accml.custom.epics.bluesky_measurement_execution_engine import BlueskyMeasurementExecutionEngine

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
    # db = catalog["heavy_local"]
    # RE.subscribe(db.v1.insert)
    # TODO: need to address live plots
    #   here a databroker should be added so that data can be accessed
    #   later on

    yp, __, _ = load_managers()
    tune(
       quadrupole_names=[name for name in yp.tune_correction_quadrupole_names()],
       measurement_values=[0, 1e-5, 0, -1e-5, 0],
       mexec=BlueskyMeasurementExecutionEngine(run_engine=RE),
       info_signals=info_sigs
    )