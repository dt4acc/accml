from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Sequence, Optional


@dataclass
class MeasuredTuneResponseItem:
    """

    Todo:
        Compare it to tune result model
        Which should stary
    """

    #: todo: what is this value?
    setpoint: float
    #: horizontal plane
    x: float
    #: vertical plane
    y: float
    #: which repetition of this value it was measured
    #: useful when data are collected from "free running"
    #: devices. The first one needs to be ignored then
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


@dataclass
class CorrectionStat:
    mean: float
    std: float
    min: float
    max: float

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            "mean={self.mean:.3f},"
            " std={self.std:.3f},"
            " min={self.min:.3f},"
            " max={self.max:.3f}"
            ")"
        )

    def __mul__(self, other: float):
        return CorrectionStat(
            mean=self.mean * other,
            std=self.std * other,
            max=self.max * other,
            min=self.min * other,
        )


@dataclass
class Tune:
    """
    Todo:
        merge
         it with accml.app.tune.model.MeasuredTuneResponseItem?
    """

    #: horizontal
    x: float
    #: vertical
    y: float

    def __sub__(self, other):
        return Tune(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Tune(-self.x, -self.y)

    def __str__(self):
        return f"{self.__class__.__name__}(x={self.x:.4f}, y={self.y:.4f})"
