"""convert the values from one state space
"""
from abc import ABCMeta, abstractmethod

from ...core.model.command import Command


class CommandRewriterBase(metaclass=ABCMeta):
    """alternative:
            TranslationService
    """
    @abstractmethod
    def forward(self, command: Command) -> Command:
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def inverse(self, command: Command) -> Command:
        raise NotImplementedError("use derived class instead")
