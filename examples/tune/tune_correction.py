import jsons
import yaml
from accml.app.tune.model import TuneResponseCollection
from accml.app.tune.tune_correction import tune_correction
from accml.custom.bluesky.bluesky_measurement_execution_engine import BlueskyMeasurementExecutionEngine
from accml.custom.facility_specific.bessyii.setup import setup
from bluesky import RunEngine



def main():
    with open("tune_result.yml") as fp:
        d = yaml.load(fp, yaml.SafeLoader)

    devices = setup()
    RE = RunEngine()
    mexec = BlueskyMeasurementExecutionEngine(run_engine=RE)
    dm = jsons.load(d, TuneResponseCollection)
    tune_correction(dm, devices=devices, mexec=mexec)


if __name__ == "__main__":
    main()