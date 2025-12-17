from typing import Dict, Generic

from accml.app.tune.model import Tune
from accml.core.model.command import TransactionalCommand, Command, BehaviourOnError

from ...core.interfaces.solver.policy import PolicyBase


class TunePolicy(PolicyBase):
    def __init__(self, scale: float = 1.0):
        self.scale = scale

    def step(
        self, current_state: Tune, diff: Tune, step: Dict[str, float]
    ) -> TransactionalCommand:
        """
        Here one could adjustments to the forecast

        * if a large step has to be made, one could rather only do a small step
          as there are not too many non linarities in the model
        * for low alpha mode, one could step more cautiously then in normal mode
        """
        return TransactionalCommand(
            transaction=[
                Command(
                    id=pc_name,
                    property="delta_set_current",
                    value=value * self.scale,
                    behaviour_on_error=BehaviourOnError.stop,
                )
                for pc_name, value in step.items()
            ]
        )


__all__ = ["TunePolicy"]
