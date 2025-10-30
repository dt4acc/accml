from abc import ABCMeta, abstractmethod
from typing import Sequence

from ..model.command import Command
from .devices_facade import DevicesFacade

class MeasurementExecutionEngine(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, commands: Sequence[Command], *args) -> str:
        """
        :return: identifier to the data

        Measurement engine is responsible to store data
        as appropriate
        """
        raise NotImplementedError("use derived class instead")
