"""Demonstrator of a measurement execution engine

Todo:
    * implement full functionality

Missing features:

* handling behaviour_on_error
* how much of the accelerator access to wrap?
* hide devices behind a software multiplexer?
  In its current form quite some information will be stored
  in the databroker

"""

from bluesky import RunEngine

from ...core.interfaces.measurement_execution_engine import MeasurementExecutionEngine


class BlueskyMeasurementExecutionEngine(MeasurementExecutionEngine):
    """Demonstrator of a measurement engine as a bluesky run engine"""

    def __init__(self, run_engine: RunEngine):
        """

        Todo:
            Specify the device type
        """
        self.run_engine = run_engine

    def execute(self, plan) -> str:
        (uid,) = self.run_engine(plan)
        return uid
