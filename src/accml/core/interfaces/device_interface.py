import asyncio
import enum
from abc import abstractmethod, ABCMeta
from typing import Dict, Generic, TypeVar, Protocol

#: Todo: reference where we got the idea from
# import ophyd_async
# from ophyd_async.core import (StandardReadable)
# from bluesky.protocols import Movable, Reading


T = TypeVar("T")


class SimpleReading(Generic[T]):
    """Reading as defined by bluesky protocol

    A dictionary containing the value and timestamp of a piece of scan data"""

    #: The current value, as a JSON encodable type or numpy array
    value: T
    #: Timestamp in seconds since the UNIX epoch
    timestamp: float



class SimpleStandardReadable(metaclass=ABCMeta):
    """

    Following the ideas of ophyd, but stripped off all convienince. Just
    providing bear minimum.

    We just be able to read data. We expect it to return new data

    Todo:
        later stage: review if we just take the data that is ready
        available

    Warning:
            It deliberately does not use the convienience of an
            AsyncStatus object with all its features and whistles
            These are to be handled by the layer using this interface
    """

    @abstractmethod
    async def read(self) -> dict[str, SimpleReading]:
        pass


T_co = TypeVar("T_co", contravariant=True)
class SimpleMovable(Protocol[T_co]):
    """

    Credit: bluesky protocal
    """
    @abstractmethod
    # async def set(self, *args: Unpack[tuple[T_co]]) -> None:
    async def set(self, *args) -> None:
        """

        uses directly asyncio
        returns None by default
        any error should return into an exception
        """


class SimpleStageAble(metaclass=ABCMeta):
    @abstractmethod
    async def stage(self):
        await asyncio.sleep(0.0)

    @abstractmethod
    async def unstage(self):
        await asyncio.sleep(0.0)


class SimpleDevice(SimpleStandardReadable, SimpleStageAble, metaclass=ABCMeta):
    """Any device needs to be stageable and readable
    """


U = TypeVar("U")

class ProvidesReferenceValue(Generic[U], metaclass=ABCMeta):
    @abstractmethod
    def get_reference_value(self) -> U:
        pass

    @abstractmethod
    def get_current_value(self) -> U:
        pass

