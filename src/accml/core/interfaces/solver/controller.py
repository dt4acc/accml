from abc import ABCMeta, abstractmethod
from typing import Sequence, Union

from accml.core.model.command import Command, ReadCommand


class ControllerInterface(metaclass=ABCMeta):
    """
    """
    @abstractmethod
    async def continuous(
            self,
            *,
            read_commands: Sequence[ReadCommand],
            set_commands: Sequence[Command],
            n_steps: Union[int,None]=None,
    ):
        """
        Args:
            read_commands: commands to retrieve the observed positions
            set_commands:  commands to set the actuators. Note that
                           a copy of the command will be made and the
                           value will be adapted
            n_steps: if set to None, run forever, otherwise run
                     maximum number of steps and stop then
        """
        raise NotImplementedError("use derived class instead")
