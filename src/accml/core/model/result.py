import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import Sequence

from accml.core.model.command import ReadCommand, Command

@dataclass
class SingleFloat:
    value : float


@dataclass
class SingleReading:
    """

    e.g. reading from one device or tune of the machine
    """
    name: str
    payload: object
    cmd: ReadCommand

    @classmethod
    def from_jsons(cls, obj):
        name = obj["name"]
        payload = obj["payload"]
        cmd = obj["cmd"]
        return cls(name=name, payload=payload, cmd=cmd)


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



def single_reading_deserializer(obj: dict, cls, **kwargs):
    assert cls == SingleReading, "only prepared to handle single reading"
    return cls.from_jsons(obj)


def dataclass_delegate_to_jsons_method(obj, **kwargs):
    import jsons
    r =  jsons.dump(obj.to_jsons(), **kwargs)
    return r


def register_deserializers_to_json_fork(t_fork):
    import jsons
    jsons.set_deserializer(single_reading_deserializer, SingleReading, high_prio=True, fork_inst=t_fork)


def register_serializers_to_json_fork(t_fork):
    import jsons
    jsons.set_serializer(dataclass_delegate_to_jsons_method, ReadTogether, high_prio=True, fork_inst=t_fork)


