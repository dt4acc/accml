import logging

from ..interfaces.state_conversion import StateConversion

logger = logging.getLogger("accml")


class EnergyDependentLinearUnitConversion(StateConversion):
    """Typical example: magnet parameters"""

    def __init__(self, *, intercept: float, slope: float, brho: float):
        self.intercept = intercept
        self.slope = slope
        self.brho = brho

    def forward(self, state: float) -> float:
        logger.info(
            "%s.forward: brho %s, intercept %s slope %s, state %s",
            self.__class__.__name__,
            self.brho,
            self.intercept,
            self.slope,
            state,
        )
        intercept = self.intercept * self.brho
        slope = self.slope * self.brho
        return intercept + slope * state

    def inverse(self, state: float) -> float:
        logger.info(
            "%s.inverse: brho %s, intercept %s slope %s, state %s",
            self.__class__.__name__,
            self.brho,
            self.intercept,
            self.slope,
            state,
        )
        intercept = self.intercept * self.brho
        slope = self.slope * self.brho
        return (state - intercept) / slope


class LinearUnitConversion(StateConversion):
    """Typical example: tune"""

    def __init__(self, *, intercept: float, slope: float):
        self.intercept = intercept
        self.slope = slope

    def forward(self, state: float) -> float:
        logger.info(
            "%s.forward: intercept %s slope %s, state %s",
            self.__class__.__name__,
            self.intercept,
            self.slope,
            state,
        )
        return self.intercept + self.slope * state

    def inverse(self, state: float) -> float:
        logger.info(
            "%s.inverse: brho %s, intercept %s slope %s, state %s",
            self.__class__.__name__,
            self.brho,
            self.intercept,
            self.slope,
            state,
        )
        return (state - self.intercept) / self.slope
