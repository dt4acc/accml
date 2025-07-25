from enum import Enum
from typing import Sequence, Union

from ...core.interfaces.yellow_pages import YellowPagesBase


class FamilyName(Enum):
    quadrupoles = "quadrupoles"
    tune_correction_quadrupoles = "tune_correction_quadrupoles"
    master_clock = "master_clock"


class YellowPages(YellowPagesBase):
    """
        or use:
        get(family_name: str)
        separate yellow pages for lattice elements and devices
    """

    def __init__(self, d: dict):
        self._d = d

    def get(self, family_name: Union[str, FamilyName]) -> Sequence[str]:
        # check for valid key?
        # key = str(FamilyName(family_name))
        return self._d[family_name]

    def quadrupole_names(self) -> Sequence[str]:
        return self.get("quadrupoles")

    def tune_correction_quadrupole_names(self) -> Sequence[str]:
        return self.get("tune_correction_quadrupoles")
