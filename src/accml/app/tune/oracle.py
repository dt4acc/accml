from typing import Dict

import numpy as np
from accml.app.tune.model import TuneResponseCollection
from accml.core.interfaces.solver.oracle import Oracle
from scipy.linalg import pinv

from accml.custom.simulators.model.tune import Tune


class TuneOracle(Oracle):
    """Tune oracle as a pure integral proportional controller"""

    def __init__(self, *, target: Tune, col: TuneResponseCollection):
        self.col = col

        self.target = target

        # currents only change from current state
        self.pc_names = None
        self.currents_cache = None

        self.Xinv = None
        self.X = None

        self._prepare()

    def _prepare(self):
        self.pc_names = [item.pc_name for item in self.col.col]
        self.currents_cache = {pc_name: 0.0 for pc_name in self.pc_names}
        # fmt:off
        self.X = np.vstack([
            [item.x.mean for item in self.col.col],
            [item.y.mean for item in self.col.col]
        ])
        # fmt:on
        self.Xinv = pinv(self.X)

    def ask(self, inp: Tune) -> (Tune, Dict[str, float]):
        """
        Returns the values to apply to the correction
        """
        assert self.Xinv is not None, "Xinv is None, did you call prepare?"
        assert self.X is not None, "X is None, did you call prepare?"

        dT = -(inp - self.target)
        dI = np.dot(self.Xinv, [dT.x, dT.y])

        # Implement it as an pure integral regulator
        currents = {
            pc_name: value + self.currents_cache[pc_name]
            for pc_name, value in zip(self.pc_names, dI)
        }
        self.currents_cache = currents
        return dT, currents


__all__ = ["TuneOracle"]
