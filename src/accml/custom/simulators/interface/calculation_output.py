"""Standardised output "elements" of the calculation engine

Output of the calculation engine can be requested with
the same interface

"""
from abc import ABCMeta, abstractmethod

from accml.app.tune.model import Tune as TuneModel


class Tune(metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> TuneModel:
        """
        Returns tune model
        """
        raise NotImplementedError("use derived class instead")
