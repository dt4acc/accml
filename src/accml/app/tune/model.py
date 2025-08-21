from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Sequence, Literal


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
