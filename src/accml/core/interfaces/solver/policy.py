from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")
U = TypeVar("U")


class PolicyBase(metaclass=ABCMeta):
    """
    Todo:
        should it use different method names than the
        
    """
    @abstractmethod
    def step(self, current_state: Generic[T], diff: Generic[T], step: Generic[U]) -> U:
        raise NotImplementedError("use derived method instead")