from collections import defaultdict
from itertools import zip_longest
from typing import Dict, Sequence

import numpy as np
from bact_math_utils.linear_fit import x_to_cov, cov_to_std
from scipy.linalg import lstsq

from .model import (
    MeasuredTuneResponseItem,
    MeasuredTuneResponsePerPowerConverter,
    MeasuredTuneResponse,
    TuneResponse,
    RandomVariableMomenta,
    TuneResponseCollection,
)
from bact_math_utils.misc import CountSame


def data_to_model(data: Dict[str, Sequence[float]]) -> MeasuredTuneResponse:
    # combine data per magnet
    tmp = defaultdict(list)

    cs = CountSame()
    for dev_name, val, tune_x, tune_y, rep in zip_longest(
        data["device_name"],
        data["channel_value"],
        data["tune-x-sig"],
        data["tune-y-sig"],
        cs(zip(data["device_name"], data["channel_value"]))
    ):

        tmp[str(dev_name)].append(
            MeasuredTuneResponseItem(value=float(val), x=float(tune_x), y=float(tune_y), repetition=rep[0])
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
    X = np.vstack([np.ones(len(indep)), indep]).T
    p, res, rnk, s = lstsq(X, dep)
    dp = cov_to_std(x_to_cov(X, res, N=len(indep), p=2))
    return RandomVariableMomenta(mean=float(p[1]), std=float(dp[1]))


def fit_one_power_converter(data: MeasuredTuneResponsePerPowerConverter):
    vals = [item.value for item in data.col]
    xrm = fit_line(vals, [item.x for item in data.col])
    yrm = fit_line(vals, [item.y for item in data.col])
    return TuneResponse(pc_name=data.pc_name, x=xrm, y=yrm)


def select_repetitions(data: MeasuredTuneResponsePerPowerConverter, acceptable_repetition: Sequence[int]) -> MeasuredTuneResponsePerPowerConverter:
    """Filter out the acceptable data using repetition

    For BESSY II e.g. the Tune measurement is free running, thus the first
    value taken can be correct, but not necessarily. So the race condition is avoided taken
    only acceptable repetitions
    """
    return MeasuredTuneResponsePerPowerConverter(
        pc_name=data.pc_name,
        col=[item for item in data.col if item.repetition in acceptable_repetition]
    )


def tune_response_analysis(data: Dict[str, Sequence[float]], acceptable_repetition=(1, 2, 3)):
    prep_data = data_to_model(data)
    sel_data = MeasuredTuneResponse(
        col=[
            select_repetitions(data=t_col, acceptable_repetition=acceptable_repetition)
            for t_col in prep_data.col
        ]
    )

    return TuneResponseCollection(
        col=[fit_one_power_converter(data) for data in sel_data.col]
    )
