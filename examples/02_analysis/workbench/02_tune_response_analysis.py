import json
from dataclasses import asdict
from pathlib import Path

import jsons
from pydantic_numpy.model import yaml

import accml.work_bench as wb
import accml.work_bench.all as wba
import accml.work_bench.app.tune

data_dir = Path(__name__).absolute().parent.parent.parent


def data_from_simple_storage(filename: str):
    """convert data stored in simple storage to data model
    """
    from accml.app.tune.preprocess_simple_storage_data import data_to_model

    with open(filename) as fp:
        data = json.load(fp)

    return data_to_model(jsons.load(data, wba.Result))


def data_from_data_broker(catalog_name: str, uid: str):
    """convert data from intake catalog to data model
    """
    from databroker import catalog
    import accml.work_bench.custom.bluesky
    from accml.app.tune.bluesky.preprocess_databroker_data import data_to_model

    db = catalog["heavy_local"]
    run = db[uid]
    data = run.primary.read()

    # just strip off all the extra information an xarray would provide
    d = {
        "device_name": data["device_name"].data,
        "channel_value": data["channel_value"].data,
        "tunes": [jsons.load(obj, wba.Tune) for obj in data["tune-transversal"].data],
    }
    data_ = data_to_model(d)
    data = wb.custom.bluesky.select_repetitions(data_, acceptable_repetition=(1, 2, 3, 4, 5))
    return data


def main():
    simulation = True
    ophyd_async_read = False
    if simulation:
        prep_data = data_from_simple_storage(data_dir / "04_measurement_simulation_data"/"tune_response_data_from_simulator.json")
        save_file = data_dir / "03_reference_data" / "tune_response_from_simulation.yml"
    elif ophyd_async_read:
        prep_data = data_from_simple_storage(
            data_dir / "04_measurement_simulation_data" / "tune_response_data_with_ophyd_async.json"
        )
        save_file = data_dir / "03_reference_data"/ "tune_response_from_measurement_w_ophyd_async.yml"
    else:
        # Todo: enter the uuid that bluesky measurement showed
        prep_data = data_from_data_broker("heavy_local", uid="a8bb94fb")
        save_file = "../../work_bench/tune/tune_response_from_twin.yml"

    result = wb.app.tune.tune_response_analysis(prep_data)
    tmp = jsons.dump(asdict(result))
    with open(save_file, "wt") as fp:
        yaml.dump(tmp, fp)


if __name__ == "__main__":
    main()
