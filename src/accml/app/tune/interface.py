from abc import abstractmethod, ABCMeta

from ...core.interfaces.measurement_execution_engine import MeasurementExecutionEngine
from ...core.interfaces.solver.controller import ControllerInterface
from ...core.interfaces.solver.oracle import Oracle
from ...core.interfaces.solver.policy import PolicyBase


class TuneControllerInterface(ControllerInterface, metaclass=ABCMeta):
    @abstractmethod
    def __init__(
        self,
        *,
        mexec: MeasurementExecutionEngine,
        oracle: Oracle,
        policy: PolicyBase,
        num_readings: int,
        wait_before_read: float,
        delay: float,
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
