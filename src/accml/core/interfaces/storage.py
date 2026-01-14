from abc import ABCMeta, abstractmethod


class StorageInterface(metaclass=ABCMeta):
    @abstractmethod
    def get(self, key) -> object:
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def add(self, key) -> str:
        """return identifier for the object stored
        """
        raise NotImplementedError("use derived class instead")
