from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

T = TypeVar("T")


# Todo: check for ABCMetaclass
class Repository(ABC, Generic[T]):
    @abstractmethod
    def load(self) -> Sequence[T]:
        pass
