from dataclasses import asdict

from accml.app.tune.bluesky.preprocess_databroker_data import select_repetitions
from accml.app.tune.tune_response_analysis import tune_response_analysis
import json
import jsons
import yaml

from accml_lib.core.model.output.result import Result, register_deserializer_for_single_reading, ResultOfExecutionStep, \
    ReadTogether, SingleReading, register_serializer_for_read_together
from accml_lib.core.model.utils.command import register_deserializer_for_command as register_cmd_deserializer
from accml_lib.core.model.output.tune import Tune

jsons_fork = jsons.fork()
register_deserializer_for_single_reading(jsons_fork)
register_serializer_for_read_together(jsons_fork)
register_cmd_deserializer(jsons_fork)

def data_from_simple_storage(filename: str):
    """convert data stored in simple storage to data model
    """
    from accml.app.tune.preprocess_simple_storage_data import data_to_model

    with open(filename) as fp:
        data = json.load(fp)

    return data_to_model(jsons.load(data, Result, fork_inst=jsons_fork))


def data_from_data_broker(catalog_name: str, uid: str):
    """convert data from intake catalog to data model
    """
    from databroker import catalog
    from accml.app.tune.bluesky.preprocess_databroker_data import data_to_model

    db = catalog["heavy_local"]
    run = db[uid]
    data = run.primary.read()

    # just strip off all the extra information an xarray would provide
    d = {
        "device_name": data["device_name"].data,
        "channel_value": data["channel_value"].data,
        "tunes": [jsons.load(obj, Tune) for obj in data["tune-transversal"].data],
    }
    data_ = data_to_model(d)
    data = select_repetitions(data_, acceptable_repetition=(1, 2, 3, 4, 5))
    return data


def main():
    simulation = True
    ophyd_async_read = False
    if simulation:
        prep_data = data_from_simple_storage("tune_response_data_from_simulator.json")
        save_file = "tune_response_from_simulation.yml"
    elif ophyd_async_read:
        prep_data = data_from_simple_storage("ophyd_async_based/tune_response_data_with_ophyd_async.json")
        save_file = "tune_response_from_measurement_w_ophyd_async.yml"
    else:
        prep_data = data_from_data_broker("heavy_local", uid="a8bb94fb")
        save_file = "tune_response_from_twin.yml"

    result = tune_response_analysis(prep_data)
    tmp = jsons.dump(asdict(result))
    with open(save_file, "wt") as fp:
        yaml.dump(tmp, fp)


if __name__ == "__main__":
    main()
