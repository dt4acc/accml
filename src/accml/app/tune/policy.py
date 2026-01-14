from typing import Dict

from ...core.interfaces.solver.policy import PolicyBase
from .model import Tune


class TunePolicy(PolicyBase):
    def __init__(self, scale: float = 1.0):
        self.scale = scale

    def step(
        self, current_state: Tune, diff: Tune, step: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Here one could adjustments to the forecast

        * if a large step has to be made, one could rather only do a small step
          as there are not too many non linarities in the model
        * for low alpha mode, one could step more cautiously then in normal mode
        """
        return {pc_name: value * self.scale for pc_name, value in step.items()}


__all__ = ["TunePolicy"]
