from accml.app.tune.preprocess_simple_storage_data import data_to_model
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
    prep_data  = data_to_model(data)

    result = tune_response_analysis(prep_data)
    tmp = jsons.dump(result, Result)
    # Todo: currently a hack ... need to foresee appropriate methods at the data class
    del tmp["_dict"]
    with open("tune_result.yml", "wt") as fp:
        yaml.dump(tmp, fp)



if __name__ == "__main__":
    main()