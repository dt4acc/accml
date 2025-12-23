from accml.app.tune.tune_response_analysis import tune_response_analysis
import json
import jsons
import yaml

from accml.core.model.result import Result, register_deserializers_to_json_fork

jsons_fork = jsons.fork()
register_deserializers_to_json_fork(jsons_fork)


def main():
    with open("data_storage.json") as fp:
        data = json.load(fp)

    data = jsons.load(data, Result, fork_inst=jsons_fork)
    data
    # just strip off all the extra information an xarray would provide
    d = {
        "device_name": data["device_name"].data,
        "channel_value": data["channel_value"].data,
        "tune-x-sig": data["tune-x-sig"].data,
        "tune-y-sig": data["tune-y-sig"].data
    }

    result = tune_response_analysis(d)
    tmp = jsons.dump(result, Result)
    # Todo: currently a hack ... need to foresee appropriate methods at the data class
    del tmp["_dict"]
    with open("tune_result.yml", "wt") as fp:
        yaml.dump(tmp, fp)



if __name__ == "__main__":
    main()