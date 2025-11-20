from dataclasses import dataclass

from pydantic import BaseModel
from typing import Hashable, Sequence

from .curve import CurveBasedConversionInfo


class EnergyDependentConversionModel(BaseModel):
    """Energy-dependent conversion model for magnetic objects.

    Todo:
        - Add metadata describing the units
    """

    intercept: float  # y-intercept of the calibration curve
    slope: float  # slope of the calibration curve
    conversion_type: str  # e.g., 'linear'


@dataclass
class Magnet:
    elem_id: str
    dev_id: str
    power_converter_id: str
    type: str
#    subtype: str
#    name: str
    forward_curve: CurveBasedConversionInfo = None
    backward_curve: CurveBasedConversionInfo = None
    pc: str = ""