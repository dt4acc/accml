from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Sequence, Union


class BehaviourOnError(IntEnum):
    stop = 1
    ignore = 2
    roll_back = 3


@dataclass
class Command:
    """
    Todo:
        how to handle the devices that should be read back?
    """
    #: can be the identifier of a lattice element or a device
    id: str
    property: str
    value: object
    behaviour_on_error: BehaviourOnError


@dataclass
class TransactionalCommand:
    transaction: Sequence[Command]


@dataclass
class CommandSequence:
    """These commands are expected to be executed on by one
    """
    commands: Sequence[TransactionalCommand]



__all__ = ["BehaviourOnError", "Command", "CommandSequence"]
