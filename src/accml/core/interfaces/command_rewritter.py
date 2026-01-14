"""convert the values from one state space
"""
from abc import ABCMeta, abstractmethod
from typing import Sequence

from ...core.model.command import Command, ReadCommand


class CommandRewriterBase(metaclass=ABCMeta):
    """alternative:
            TranslationService
    """
    @abstractmethod
    def forward(self, command: Command) -> Sequence[Command]:
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def inverse(self, command: Command) -> Sequence[Command]:
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def forward_read_command(self, command: ReadCommand) -> Sequence[ReadCommand]:
        """Typically an answer of liaison manager"""
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def inverse_read_command(self, command: ReadCommand) -> Sequence[ReadCommand]:
        """Typically an answer of liaison manager"""
        raise NotImplementedError("use derived class instead")
