from functools import cached_property
from typing import Sequence, Tuple, Literal

import numpy as np

#: todo shall we install it from numpy.dual
from numpy.linalg import lstsq

from .model import (
    TuneResponseForFit,
    TuneCorrectionCurrent,
    TuneResponse,
    TuneResponseForFitItem,
)


class TuneCorrectionOracle:
    """
    Todo: make interface coherent to scikit learn linear regression
          interface as much as reasonable

          Consi
    """

    def __init__(self, data: TuneResponseForFit):
        self.data = data

    @cached_property
    def _fit_data(self):
        data = self.data
        self.x_pol = np.array([item.polarity for item in data.x])
        self.y_pol = np.array([item.polarity for item in data.y])
        self.x_from_x = np.array([item.response.x.mean for item in data.x]) * self.x_pol
        self.x_from_y = np.array([item.response.x.mean for item in data.y]) * self.y_pol
        self.y_from_x = np.array([item.response.y.mean for item in data.x]) * self.x_pol
        self.y_from_y = np.array([item.response.y.mean for item in data.y]) * self.y_pol

        return dict(
            x=np.array([self.x_from_x, self.x_from_y]).T,
            y=np.array([self.y_from_x, self.y_from_y]).T,
        )
        # self.names = [item.pc_name for item  in col]

    def predict(self, dx, dy) -> Sequence[TuneCorrectionCurrent]:
        r = self._fit_data
        # delete me .. just for debug purposes
        rscaled = dict(x=r["x"] * 1e3, y=r["y"] * 1e3)
        Ascaled = np.vstack([rscaled["x"], rscaled["y"]])
        A = np.vstack([r["x"], r["y"]])
        b_prep = [np.ones(len(r["x"])) * dx, np.ones(len(r["y"])) * dy]
        b = np.hstack(b_prep)
        coeffs, residuals, rank, s = lstsq(A, b)
        assert rank == 2
        # Todo: make it a random variable, compute deviations
        # Todo: shall one store fit data as metadata?
        coeff_x = float(coeffs[0])
        coeff_y = float(coeffs[1])

        return [
            TuneCorrectionCurrent(
                pc_name=item.response.pc_name, delta_current=item.polarity * coeff_x
            )
            for item in self.data.x
        ] + [
            TuneCorrectionCurrent(
                pc_name=item.response.pc_name, delta_current=item.polarity * coeff_y
            )
            for item in self.data.y
        ]


def enrich_with_polarity(data: Tuple[str, TuneResponse]) -> TuneResponseForFit:
    def polarity(value) -> Literal[1, -1]:
        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            raise AssertionError(
                "computing polarity: data was neither larger nor smaller than 0"
            )

    r = TuneResponseForFit(
        y=[
            TuneResponseForFitItem(polarity=polarity(item.y.mean), response=item)
            for plane, item in data
            if plane == "y"
        ],
        x=[
            TuneResponseForFitItem(polarity=polarity(item.x.mean), response=item)
            for plane, item in data
            if plane == "x"
        ],
    )
    return r
