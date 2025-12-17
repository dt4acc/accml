from dataclasses import asdict

from accml.app.tune.tune_response_analysis import (
    tune_response_analysis,
    quality_factor_as_txt,
)
from databroker import catalog
import jsons
import yaml


def main():
    db = catalog["heavy_local"]
    uid = "9ca0f190-8792-4cc3-a0f5-2883008c9aa7"
    run = db[uid]
    data = run.primary.read()

    # just strip off all the extra information an xarray would provide
    d = {
        "device_name": data["device_name"].data,
        "channel_value": data["channel_value"].data,
        "tune-x-sig": data["tune-x-sig"].data,
        "tune-y-sig": data["tune-y-sig"].data,
    }

    result = tune_response_analysis(d, acceptable_repetition=(1, 2, 3))
    txt = "\n".join(quality_factor_as_txt(result))
    print(
        f"""Tune quality factors for uid {uid}

{txt}

ratio: tune in family versus other plane
dr:    estimate of ratio error based on fit of tune shift (covar -> std)
"""
    )

    tmp = jsons.dump(asdict(result))
    # Todo: currently a hack ... need to foresee appropriate methods at the data class
    with open("tune_result.yml", "wt") as fp:
        yaml.dump(tmp, fp)


if __name__ == "__main__":
    main()
