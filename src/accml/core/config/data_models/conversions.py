""" Configuration classes for conversions."""

# TODO: add different type of conversion models here

from abc import ABC
from pydantic import BaseModel

class ConversionConfig(BaseModel, ABC):
    pass


class EnergyDependentConversionModel(ConversionConfig):
    """Energy-dependent conversion model for magnetic objects.

    Todo:
        - Add metadata describing the units
    """

    intercept: float  # y-intercept of the calibration curve
    slope: float  # slope of the calibration curve
    conversion_type: str  # e.g., 'linear'

