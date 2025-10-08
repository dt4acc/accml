from abc import ABCMeta, abstractmethod
from typing import Sequence, Dict

from accml.core.model.command import Command


class MeasurementExecutionEngine(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, commands: Sequence[Command], *args) -> str:
        """
        :return: identifier to the data

        Measurement engine is responsible to store data
        as appropriate

        Todo:
            Review how to include transactional commands
        """
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def setup(self, *args) -> None:
        """
        Setup the measurement execution engine

        Todo:
            Review if this method should exist at all
            Rather remove it
        """
        raise NotImplementedError("use derived class instead")