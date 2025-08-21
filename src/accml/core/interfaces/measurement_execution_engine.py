from abc import ABCMeta, abstractmethod
from typing import Sequence

from accml.core.model.command import Command


class MeasurementExecutionEngine(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, commands: Sequence[Command], *args) -> str:
        """
        :return: identifier to the data

        Measurement engine is responsible to store data
        as appropriate
        """
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def correction_step(self, *, oracle, policy, detectors, actuators, **kwargs) -> str:
        """
        Todo:
            should that be rather on a higher level ?
            Need to add policy maker
        """

    @abstractmethod
    def setup(self, *args) -> None:
        """
        Setup the measurement execution engine
        """
        raise NotImplementedError("use derived class instead")