from abc import ABCMeta, abstractmethod
from typing import Sequence

from ..model.command import TransactionCommand, ReadCommand, Command
from ..model.result import SingleReading, ReadTogether


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

    @abstractmethod
    async def trigger_read(self, cmds: Sequence[ReadCommand]) -> ReadTogether:
        """Following ophyd-async / ophyd design

            Todo:
                Is this a good idea?
        """
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    async def set(self, cmds: Sequence[Command]):
        """execute these commands together"""
        raise NotImplementedError("use derived class instead")
