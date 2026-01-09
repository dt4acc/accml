from dataclasses import dataclass
from enum import IntEnum
from typing import Sequence


class BehaviourOnError(IntEnum):
    stop = 1
    ignore = 2
    roll_back = 3


@dataclass(frozen=True)
class ReadCommand:
    """Use for retrieving data"""

    id: str
    property: str


@dataclass
class Command:
    #: can be the identifier of a lattice element or a device
    id: str
    property: str
    value: object
    behaviour_on_error: BehaviourOnError


@dataclass
class TransactionCommand:
    """Commands that should be executed (more or less) at the same time

    In particular: state of the machine is only relevant *after* all
    commands have been executed
    """

    transaction: Sequence[Command]


@dataclass
class CommandSequence:
    """These commands are expected to be executed on by one"""

    commands: Sequence[TransactionCommand]


__all__ = ["BehaviourOnError", "Command", "CommandSequence", "ReadCommand", "TransactionCommand"]
