from abc import ABCMeta, abstractmethod


class Oracle(metaclass=ABCMeta):
    @abstractmethod
    def ask(self, inp: object) -> object:
        raise NotImplementedError("use derived class instead")