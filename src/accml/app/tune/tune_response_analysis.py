from collections import defaultdict
from itertools import zip_longest
from typing import Dict, Sequence

import numpy as np
from numpy.polynomial import Polynomial

from .model import (
    MeasuredTuneResponseItem,
    MeasuredTuneResponsePerPowerConverter,
    MeasuredTuneResponse,
    TuneResponse,
    RandomVariableMomenta,
    TuneResponseCollection,
)


def data_to_model(data: Dict[str, Sequence[float]]) -> MeasuredTuneResponse:
    # combine data per magnet
    tmp = defaultdict(list)
    for dev_name, val, tune_x, tune_y in zip_longest(
        data["device_name"],
        data["channel_value"],
        data["tune-x-sig"],
        data["tune-y-sig"],
    ):
        tmp[str(dev_name)].append(
            MeasuredTuneResponseItem(value=float(val), x=float(tune_x), y=float(tune_y))
        )

    # Now put it in a model
    r = MeasuredTuneResponse(
        col=[
            MeasuredTuneResponsePerPowerConverter(pc_name=dev_name, col=items)
            for dev_name, items in tmp.items()
        ]
    )
    return r


def fit_line(indep: Sequence[float], dep: Sequence[float]) -> RandomVariableMomenta:
    """
    Todo:
        need to compute the standard deviation
        find out which algorithm to be used

        orbit response profits from leastsquare `lstsg` so perhaps also to use it here
    """
    coeffs, info = Polynomial.fit(indep, dep, deg=1, full=True)
    residuals, rank, singular_values, rcond = info
    return RandomVariableMomenta(mean=float(coeffs.coef[1]), std=float(np.nan))


def fit_one_power_converter(data: MeasuredTuneResponsePerPowerConverter):
    vals = [item.value for item in data.col]
    xrm = fit_line(vals, [item.x for item in data.col])
    yrm = fit_line(vals, [item.y for item in data.col])
    return TuneResponse(pc_name=data.pc_name, x=xrm, y=yrm)


def tune_response_analysis(data: Dict[str, Sequence[float]]):
    prep_data = data_to_model(data)
    return TuneResponseCollection(
        col=[fit_one_power_converter(data) for data in prep_data.col]
    )
