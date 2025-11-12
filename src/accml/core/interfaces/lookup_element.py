from abc import ABCMeta, abstractmethod
from typing import Hashable


class LookupElement(metaclass=ABCMeta):
    @abstractmethod
    def id(self) -> Hashable:
        raise AssertionError("use derived class instead")
