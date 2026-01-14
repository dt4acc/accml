from abc import ABCMeta, abstractmethod


class Oracle(metaclass=ABCMeta):
    """Forecast of what should be done

    Alternative names: Model (similar to control theory)

    This interface only uses ask instead of tell/ask.
    It combines these to a simple ask
    """

    @abstractmethod
    def ask(self, inp: object) -> object:
        raise NotImplementedError("use derived class instead")
