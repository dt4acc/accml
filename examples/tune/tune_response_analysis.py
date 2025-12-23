from collections import defaultdict

from accml.app.tune.model import MeasuredTuneResponse, MeasuredTuneResponseItem, MeasuredTuneResponsePerPowerConverter
from accml.app.tune.tune_response_analysis import tune_response_analysis
import json
import jsons
import yaml

from accml.core.model.result import Result, register_deserializers_to_json_fork

jsons_fork = jsons.fork()
register_deserializers_to_json_fork(jsons_fork)

def convert_result_to_signal_stream():
    """
    Todo:
        needs to be reviewed if keep it that way
        perhaps the entry point should be
        "physics ready data"
    """


def data_to_model(data: Result) -> MeasuredTuneResponse:
    tmp = defaultdict(list)

    for single in data.data:
        tune = single.get("tune-transversal").payload
        dev_name = "unknown"
        setpoint = single.get("setpoint")
        dev_name = setpoint.cmd["id"]
        tmp[str(dev_name)].append(
            MeasuredTuneResponseItem(setpoint=float(setpoint.payload["value"]), x=float(tune["x"]), y=float(tune["y"]))
        )

    r = MeasuredTuneResponse(
        col=[
            MeasuredTuneResponsePerPowerConverter(pc_name=dev_name, col=items)
            for dev_name, items in tmp.items()
        ]
    )
    return r

def main():
    with open("data_storage.json") as fp:
        data = json.load(fp)

    data = jsons.load(data, Result, fork_inst=jsons_fork)
    prep_data  = data_to_model(data)

    result = tune_response_analysis(prep_data)
    tmp = jsons.dump(result, Result)
    # Todo: currently a hack ... need to foresee appropriate methods at the data class
    del tmp["_dict"]
    with open("tune_result.yml", "wt") as fp:
        yaml.dump(tmp, fp)



if __name__ == "__main__":
    main()