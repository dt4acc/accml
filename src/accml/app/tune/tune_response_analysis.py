from typing import Sequence

import numpy as np
from scipy.linalg import lstsq

from bact_math_utils.linear_fit import x_to_cov, cov_to_std

from .model import (
    MeasuredTuneResponsePerPowerConverter,
    TuneResponseCollection, MeasuredTuneResponse, RandomVariableMomenta, TuneResponse,
)


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
    vals = [item.setpoint for item in data.col]
    xrm = fit_line(vals, [item.x for item in data.col])
    yrm = fit_line(vals, [item.y for item in data.col])
    return TuneResponse(pc_name=data.pc_name, x=xrm, y=yrm)


def tune_response_analysis(prep_data: MeasuredTuneResponse):
    # prep_data = data_to_model(data)
    return TuneResponseCollection(
        col=[fit_one_power_converter(data) for data in prep_data.col]
    )
