
class Stepper(metaclass=ABCMeta):
    @abstractmethod
    def step(self, input: object) -> object:
        raise NotImplementedError("use derived class instead")