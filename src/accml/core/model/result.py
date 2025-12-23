import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import Sequence


@dataclass
class SingleReading:
    """

    e.g. reading from one device or tune of the machine
    """
    name: str
    payload: object

    def from_jsons(self, obj):
        pass


@dataclass
class ReadTogether:
    """
    data taken together
    """
    data : Sequence[SingleReading]

    def get(self, key):
         return self._dict[key]

    @cached_property
    def _dict(self):
          return {d.name : d for d in self.data}

    def to_jsons(self):
        return dict(name=self.__class__.__name__, data=self.data)


@dataclass
class Result:
    start: datetime.datetime
    end: datetime.datetime
    #: in the expected view / context of the caller
    data: Sequence[ReadTogether]
    #: in the expected view / context as produced by the backend
    orig_data: Sequence[ReadTogether]