from dataclasses import asdict

from accml.app.tune.tune_response_analysis import tune_response_analysis
from databroker import catalog
import jsons
import yaml


def main():
    db = catalog["heavy_local"]
    uid = '1955adfd-2f94-4459-8888-4f63cbc839de'
    uid = '2f7c28d8-f0b2-4b5f-ac9f-cc5be4acaf86'
    uid = '1e782ab8-ebd7-4bcb-bffb-ed68c1b1b011'
    run  = db[uid]
    data = run.primary.read()

    # just strip off all the extra information an xarray would provide
    d = {
        "device_name": data["device_name"].data,
        "channel_value": data["channel_value"].data,
        "tune-x-sig": data["tune-x-sig"].data,
        "tune-y-sig": data["tune-y-sig"].data
    }

    result = tune_response_analysis(d)
    tmp = jsons.dump(asdict(result))
    # Todo: currently a hack ... need to foresee appropriate methods at the data class
    with open("tune_result.yml", "wt") as fp:
        yaml.dump(tmp, fp)



if __name__ == "__main__":
    main()