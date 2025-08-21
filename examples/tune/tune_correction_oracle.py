import jsons
import yaml

from accml.app.tune.model import (
    TuneCorrectionCurrentsCollection,
    TuneResponseCollection,
    TuneResponse,
    TuneResponseForFit,
    TuneResponseForFitItem,
)
from accml.app.tune.model_io import install_jsons_io

install_jsons_io()

from accml.app.tune.tune_correction_oracle import (
    TuneCorrectionOracle,
    enrich_with_polarity,
)


def sort_quadrupole_to_plane(data: TuneResponse) -> (str, TuneResponse):
    """guess to which family or plane the quadrupoles belong to"""
    ratio = abs(data.x.mean / data.y.mean)
    # x is not that pronounced
    #    revisit when proper start data is there
    if ratio > 1.19:
        plane = "x"
    elif ratio < 1 / 2.0:
        plane = "y"
    else:
        plane = None
    return plane, data


def post_process(data: TuneResponseCollection) -> TuneResponseForFit:
    if True:
        # sort items per family so that its easier to debug ... bessy II specific
        # delete me
        col = [item for item in data.col]
        col.sort(key=lambda item: int(item.pc_name[1]) * 100 + int(item.pc_name[-2]))
    else:
        col = data.col

    # find out which quadrupole belong to which family
    # typically one will denote the different quads and store it in yp
    sorted_to = [sort_quadrupole_to_plane(item) for item in col]
    unidentified_quads = [item for plane, item in sorted_to if plane is None]
    assert len(unidentified_quads) == 0
    return enrich_with_polarity(sorted_to)


def main():
    with open("tune_result.yml") as fp:
        d = yaml.safe_load(fp)
    dm = jsons.load(d, TuneResponseCollection)
    del d
    # represent data so that it is easier to read
    data_for_fit = post_process(dm)
    d = jsons.dump(data_for_fit, TuneResponseForFit)
    d
    with open("tune_oracle_data.yml", "wt") as fp:
        d = yaml.dump(d, fp)
    del d, data_for_fit
    with open("tune_oracle_data.yml") as fp:
        d = yaml.safe_load(fp)
    data_for_fit = jsons.load(d, TuneResponseForFit)

    fit = TuneCorrectionOracle(data_for_fit)
    r = TuneCorrectionCurrentsCollection(col=fit.predict(0.1, -0.1))
    r


if __name__ == "__main__":
    main()
