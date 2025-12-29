from abc import ABCMeta, abstractmethod
from typing import Sequence

from ..model.command import TransactionCommand


class MeasurementExecutionEngine(metaclass=ABCMeta):
    @abstractmethod
    def execute(self, commands_collection: Sequence[TransactionCommand], **kwargs) -> str:
        """executes a sequence of Transactional Commands.

        So a number of commands are executed. At each step
        the transactional command is executed at once

        :return: identifier to the data

        Measurement engine is responsible to store data
        as appropriate
        """
        raise NotImplementedError("use derived class instead")
