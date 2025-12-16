from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Sequence, Optional


@dataclass
class MeasuredTuneResponseItem:
    value: float
    x: float
    y: float
    repetition: Optional[int] = -1


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
