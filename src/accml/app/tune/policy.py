from typing import Dict, Generic

from accml.app.tune.model import Tune

from ...core.interfaces.solver.policy import PolicyBase


class TunePolicy(PolicyBase):
    def step(self, current_state: Tune, diff: Tune, step: Dict[str, float]) -> Dict[str, float]:
        """
        Here one could adjustments to the forecast

        * if a large step has to be made, one could rather only do a small step
          as there are not too many non linarities in the model
        * for low alpha mode, one could step more cautiously then in normal mode
        """
        return step
