from abc import ABCMeta, abstractmethod
from typing import Sequence

from ..model.command import TransactionCommand


class MeasurementExecutionEngine(metaclass=ABCMeta):
    @abstractmethod
    def execute(
        self, commands_collection: Sequence[TransactionCommand], *args, **kwargs
    ) -> str:
        """
        :return: identifier to the data

        Measurement engine is responsible to store data
        as appropriate
        """
        raise NotImplementedError("use derived class instead")
