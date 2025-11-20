from dataclasses import dataclass
from typing import Sequence


@dataclass
class CurvePoint:
    indep: float
    dep: float


@dataclass
class CurveBasedConversionInfo:
    curve: Sequence[CurvePoint]
