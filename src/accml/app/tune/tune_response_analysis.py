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


def tune_response_analysis(
    data: Dict[str, Sequence[float]], acceptable_repetition=(1, 2, 3)
):
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


def data_to_model(data: Dict[str, Sequence[float]]) -> MeasuredTuneResponse:
    """put data together for each magnet"""
    tmp = defaultdict(list)

    cs = CountSame()
    for dev_name, val, tune_x, tune_y, rep in zip_longest(
        data["device_name"],
        data["channel_value"],
        data["tune-x-sig"],
        data["tune-y-sig"],
        cs(zip(data["device_name"], data["channel_value"])),
    ):

        tmp[str(dev_name)].append(
            MeasuredTuneResponseItem(
                value=float(val), x=float(tune_x), y=float(tune_y), repetition=rep[0]
            )
        )

    # Now put it in a model
    r = MeasuredTuneResponse(
        col=[
            MeasuredTuneResponsePerPowerConverter(pc_name=dev_name, col=items)
            for dev_name, items in tmp.items()
        ]
    )
    return r


def select_repetitions(
    data: MeasuredTuneResponsePerPowerConverter, acceptable_repetition: Sequence[int]
) -> MeasuredTuneResponsePerPowerConverter:
    """Filter out the acceptable data using repetition

    For BESSY II e.g. the Tune measurement is free running, thus the first
    value taken can be correct, but not necessarily. So the race condition is avoided taken
    only acceptable repetitions
    """
    return MeasuredTuneResponsePerPowerConverter(
        pc_name=data.pc_name,
        col=[item for item in data.col if item.repetition in acceptable_repetition],
    )


def fit_one_power_converter(data: MeasuredTuneResponsePerPowerConverter):
    vals = [item.value for item in data.col]
    xrm = fit_line(vals, [item.x for item in data.col])
    yrm = fit_line(vals, [item.y for item in data.col])
    return TuneResponse(pc_name=data.pc_name, x=xrm, y=yrm)


def fit_line(indep: Sequence[float], dep: Sequence[float]) -> RandomVariableMomenta:
    """ """
    X = np.vstack([np.ones(len(indep)), indep]).T
    p, res, rnk, s = lstsq(X, dep)
    dp = cov_to_std(x_to_cov(X, res, N=len(indep), p=2))
    return RandomVariableMomenta(mean=float(p[1]), std=float(dp[1]))


def quality_factor_as_txt(col: TuneResponseCollection) -> Sequence[str]:
    r = [quality_factor(item) for item in col.col]
    r.sort(key=lambda item: ord(item["family"][0]) * 1000 + item["ratio"])
    return [
        f"{item['family']:3s} {item['pc_name']:8s}: r = {item['ratio']:.2f} +/- {item['dr']:.3f}"
        for item in r
    ]


def quality_factor(data: TuneResponse) -> Dict[str, float]:
    """ratio of tune in x and y along with its error"""
    ratio = data.x.mean / -data.y.mean
    family = "x"
    if abs(ratio) < 1:
        ratio = 1.0 / ratio
        family = "y"
        dr = abs(data.y.std / data.x.mean) + abs(data.x.std / data.x.mean ** 2)
    else:
        dr = abs(data.x.std / data.y.mean) + abs(data.y.std / data.y.mean ** 2)
    return dict(pc_name=data.pc_name, family=family, ratio=ratio, dr=dr)


__all__ = ["tune_response_analysis", "quality_factor_as_txt"]
