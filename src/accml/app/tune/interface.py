from abc import abstractmethod, ABCMeta

from accml_lib.core.interfaces.utils.measurement_execution_engine import MeasurementExecutionEngine
from accml_lib.core.interfaces.solver.controller import ControllerInterface
from accml_lib.core.interfaces.solver.oracle import Oracle
from accml_lib.core.interfaces.solver.policy import PolicyBase


class TuneControllerInterface(ControllerInterface, metaclass=ABCMeta):
    @abstractmethod
    def __init__(
        self,
        *,
        mexec: MeasurementExecutionEngine,
        oracle: Oracle,
        policy: PolicyBase,
        num_readings: int,
        wait_after_set: float,
        wait_between_samples: float,
        logger,
    ):
        """
        Todo:
            Review if this interface is general enough so that it
            should be part of the controller interface

            Review if read and set-commands should be already
            declared here
        """
        raise NotImplementedError("use derived class instead")
