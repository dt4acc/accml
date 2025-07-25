from abc import ABCMeta, abstractmethod

from ...core.model.identifiers import DevicePropertyID, LatticeElementPropertyID


class LiaisonManagerBase(metaclass=ABCMeta):
    """transforms pairs of (id, property)

    Warning:
        it returns a sequence of device / properties
        More than one device can be necessary to be updated

    """

    @abstractmethod
    def forward(self, id_: LatticeElementPropertyID) -> DevicePropertyID:
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def inverse(self, id_: DevicePropertyID) -> LatticeElementPropertyID:
        raise NotImplementedError("use derived class instead")
