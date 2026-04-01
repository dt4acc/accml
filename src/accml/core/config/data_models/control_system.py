""" Configuration classes for control system."""

from abc import ABC
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ControlSystemConfig(BaseModel, ABC):
    pass


class TANGOConfig(ControlSystemConfig):
    host: str


class EPICSType(Enum):

    CA = 'CA' # Channel Access
    PV = 'PV' # PV Access


class EPICSConfig(ControlSystemConfig):
    access_type: EPICSType
    pv_prefix: Optional[str] = ""


class DOOCSConfig(ControlSystemConfig):
    pass
