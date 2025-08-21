from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Dict, Sequence, Literal

import jsons


@dataclass
class MeasuredTuneResponseItem:
    value: float
    x: float
    y: float


@dataclass
class MeasuredTuneResponsePerPowerConverter:
    pc_name: str
    col: Sequence[MeasuredTuneResponseItem]


@dataclass
class MeasuredTuneResponse:
    col: Sequence[MeasuredTuneResponsePerPowerConverter]

    def get(self, name) -> MeasuredTuneResponsePerPowerConverter:
        return self._dict[name]

    @cached_property
    def _dict(self) -> Dict[str, MeasuredTuneResponsePerPowerConverter]:
        return {item.pc_name: item for item in self.col}


@dataclass
class RandomVariableMomenta:
    mean: float
    std: float


@dataclass
class TuneResponse:
    pc_name: str
    x: RandomVariableMomenta
    y: RandomVariableMomenta


@dataclass
class TuneResponseCollection:
    col: Sequence[TuneResponse]

    def get(self, name: str) -> TuneResponse:
        return self._dict[name]

    @cached_property
    def _dict(self) -> Dict[str, TuneResponse]:
        return {item.pc_name: item for item in self.col}


@dataclass
class TuneResponseForFitItem:
    polarity: Literal[1, -1]
    response: TuneResponse


@dataclass
class TuneResponseForFit:
    x: Sequence[TuneResponseForFitItem]
    y: Sequence[TuneResponseForFitItem]


@dataclass
class TuneCorrectionCurrent:
    pc_name: str
    delta_current: float


@dataclass
class TuneCorrectionCurrentsCollection:
    col: Sequence[TuneCorrectionCurrent]

    def get(self, name: str) -> TuneCorrectionCurrent:
        return self._dict[name]

    @cached_property
    def _dict(self) -> Dict[str, TuneCorrectionCurrent]:
        return {item.pc_name: item for item in self.col}


def serialise_tune_response_collection(inst: TuneResponseCollection, **kwargs) -> Dict:
    assert isinstance(inst, TuneResponseCollection)
    r = dict(col=jsons.dump(inst.col, **kwargs))
    return r


def serialise_tune_response_for_fit_item(
    inst: TuneResponseForFitItem, **kwargs
) -> Dict:
    """
    required as polarity is defined as a Literal

    Todo:
        shall it be a cls method of TuneResponseForFitItem?
    """
    assert isinstance(inst, TuneResponseForFitItem)
    return dict(
        response=jsons.dump(inst.response, **kwargs), polarity=int(inst.polarity)
    )


def deserialise_tune_response_for_fit_item(
    inp: Dict, *args, **kwargs
) -> TuneResponseForFitItem:
    """
    required as polarity is defined as a Literal

    Todo:
        shall it be a cls method of TuneResponseForFitItem?
    """
    return TuneResponseForFitItem(
        polarity=int(inp["polarity"]),
        response=jsons.load(inp["response"], TuneResponse),
    )


# todo: shall these serializers only be installed on user request ?
#       is it straight forward to uninstall them if needed
jsons.set_serializer(serialise_tune_response_for_fit_item, TuneResponseForFitItem)
jsons.set_deserializer(deserialise_tune_response_for_fit_item, TuneResponseForFitItem)
jsons.set_serializer(serialise_tune_response_collection, TuneResponseCollection)
