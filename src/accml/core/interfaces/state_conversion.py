from abc import abstractmethod, ABCMeta


class StateConversion(metaclass=ABCMeta):
    """convert one state to an other

    Other wide spread names:
    * unit conversion
    * coordinate system transformation

    Please note initialisation is not handled here

    """

    @abstractmethod
    def forward(self, state: object) -> object:
        """from "physics" to machine

        Follows bluesky convention
        """
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def inverse(self, state: object) -> object:
        """from machine to "physics"

        Follows bluesky convention
        """
        raise NotImplementedError("use derived class instead")
