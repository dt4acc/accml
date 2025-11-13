""" Configuration class for accelerator and families."""

from pydantic import BaseModel
from typing import Dict, List, Optional, Hashable
from .control_system import ControlSystemConfig
from .simulator import SimulatorConfig
from .device import DeviceConfig

class AcceleratorConfig(BaseModel):

    facility: Optional[str]
    machine: str
    # TODO: data_storage
    controls: Optional[Dict[Hashable, ControlSystemConfig]] = None
    simulators: Optional[Dict[Hashable, SimulatorConfig]] = None
    devices: Optional[Dict[Hashable, DeviceConfig]] = None
    families: Optional[Dict[Hashable, List[Hashable]]] = None
    # TODO: operational_modes


class FamilyConfig(BaseModel):
    name: Hashable
    devices: list[Hashable]
    