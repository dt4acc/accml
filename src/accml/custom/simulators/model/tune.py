"""

Todo:
    merge it with app?
    move it to core?
"""
from dataclasses import dataclass


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
