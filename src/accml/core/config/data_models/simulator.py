""" Configuration classes for simulators."""

from pydantic import BaseModel
from enum import Enum

class SimulationEngine(Enum):
    PYAT = 'pyat'


class SimulatorConfig(BaseModel):
    type: SimulationEngine
    model: str  # Path to the lattice model.