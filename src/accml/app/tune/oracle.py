from typing import Dict

import numpy as np
from accml.app.tune.model import Tune, TuneResponseCollection
from accml.core.interfaces.solver.oracle import Oracle
from scipy.linalg import pinv


class TuneOracle(Oracle):
    """
    """
    def __init__(self, *, reference: Tune, x: TuneResponseCollection, y: TuneResponseCollection):
        self.x = x
        self.y = y
        self.ref = reference
        self.Xinv = None
        self.X = None
        self.pc_names = None

        self._prepare()

    def _prepare(self):
        self.pc_names = [item.pc_name for item in self.x.col] + [item.pc_name for item in self.y.col]
        self.X = np.vstack([
            [item.x.mean for item in self.x.col] + [item.x.mean for item in self.y.col],
            [item.y.mean for item in self.x.col] + [item.y.mean for item in self.y.col],
        ])
        self.Xinv = pinv(self.X)

    def ask(self, inp: Tune) -> (Tune, Dict[str, float]):
        """
        Returns the values to apply to the correction
        """
        assert self.Xinv is not None, "Xinv is None, did you call prepare?"
        assert self.X is not None, "X is None, did you call prepare?"

        dT = inp - self.ref
        dI = np.dot(self.Xinv, [dT.x, dT.y])
        return dT, {pc_name: value for pc_name, value in zip(self.pc_names, dI)}
