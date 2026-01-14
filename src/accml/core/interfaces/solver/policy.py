from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")
U = TypeVar("U")


class PolicyBase(metaclass=ABCMeta):
    """Present a step based on current step, difference and suggest correction step"""

    @abstractmethod
    def step(self, current_state: Generic[T], diff: Generic[T], step: Generic[U]) -> U:
        raise NotImplementedError("use derived method instead")
