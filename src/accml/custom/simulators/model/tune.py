"""

Todo:
    merge it with app?
    move it to core
"""
from dataclasses import dataclass


@dataclass
class Tune:
    """
    Todo:
        more it with accml.app.tune.model.MeasuredTuneResponseItem?
    """
    #: horizontal
    x: float
    #: vertical
    y: float