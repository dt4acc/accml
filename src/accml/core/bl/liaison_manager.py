import logging
from typing import Mapping

from accml.core.interfaces.liaison_manager import LiaisonManagerBase
from accml.core.model.identifiers import LatticeElementPropertyID, DevicePropertyID

logger = logging.getLogger("accml")


class LiaisonManager(LiaisonManagerBase):
    """
    Todo:
        consider internally to represent classes of devices with a certain functionallity

        So internally have
            * classes of devices providing similar properties
            * this can be used when searching for suggesting alternatives to the
              user when searching for it

    """

    def __init__(
        self,
        forward_lut: Mapping[LatticeElementPropertyID, DevicePropertyID],
        inverse_lut: Mapping[DevicePropertyID, LatticeElementPropertyID],
    ):
        self.forward_lut = forward_lut
        self.inverse_lut = inverse_lut

    def forward(self, id_: LatticeElementPropertyID) -> DevicePropertyID:
        try:
            return self.forward_lut[id_]
        except KeyError as ke:
            logger.error(
                f"{self.__class__.__name__} id {id_} not found in lookup table: {ke}"
            )
            raise ke

    def inverse(self, id_: DevicePropertyID) -> LatticeElementPropertyID:
        try:
            return self.inverse_lut[id_]
        except KeyError as ke:
            # Todo: give the user a hint what we know and what is close to what we know
            logger.error(
                f"{self.__class__.__name__} id {id_} not found in lookup table: {ke}"
            )
            raise ke
