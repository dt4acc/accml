import asyncio
import enum
import logging
import threading

from accml.core.interfaces.backend.backend import BackendRW
from ..interface.accelerator_simulator import AcceleratorSimulatorInterface


from transitions import Machine
from ..model.tune import Tune

logger = logging.getLogger()


class States(enum.Enum):
    pending = "pending"
    executing = "executing"
    finished = "finished"
    error = "error"


class ResultElement:
    """

    """
    def get(self) -> object:
        return
# class OrbitElement
# needs to be implemented
#    pass

class TwissElement(ResultElement):
    def __init__(self, backend):
        self.backend = backend

    def get(self) -> Tune:
        return self.backend.get_twiss()


class TuneElement(ResultElement):
    def __init__(self, backend):
        self.backend = backend

    def get(self) -> Tune:
        return self.backend.get_tune()



class SimulationStateModel:
    """all methods added by class::`transitions.Machine`

    transititions used as bluesky seems not to use
    superstate machine any more
    """


class SimulatorBackend(BackendRW):
    """
    Todo:
        how far shall asynchronisity go?

    I assume today that the calculation engine is
    1. set to a state
    2. then calculations are triggered

    So the calculations shall only happen after the state was set

    It seems that setting should provide synchronous algorithms too
    """
    def __init__(self, *, acc: AcceleratorSimulatorInterface, name: str, logger=logger):
        self.acc = acc
        self.logger = logger
        self.name = name

        self.tune = None

        self.calculation_lock = threading.Lock()
        self.model = SimulationStateModel
        self.state = Machine(
            model=self.model,
            # fmt:off
            transitions=[
                dict( trigger="calculate" , source=States.pending   , dest=States.executing, before=self._clear_stored_results ),
                dict( trigger="finished"  , source=States.executing , dest=States.finished  ),
                dict( trigger="changed"   , source=States.finished  , dest=States.pending,   after=self._clear_stored_results   ),
                dict( trigger="changed"   , source=States.pending   , dest=States.pending,   after=self._clear_stored_results   ),
                dict( trigger="clear"     , source=States.error     , dest=States.pending   ),
                dict( trigger="error"     , source="*"              , dest=States.error     ),
            ],
            # fmt:on
            states=[st for st in States],
            initial=States.pending
        )

        self.result_elements = dict(twiss=TwissElement(backend=self), tune=TuneElement(backend=self))

    def _clear_stored_results(self):
        self.tune = None

    def get_natural_view_name(self):
        return "design"

    async def trigger(self, dev_id: str, prop_id: str):
        self.logger.info(
            "%s(name=%s) no trigger needed", self.__class__.__name__, self.name
        )

    async def read(self, dev_id: str, prop_id: str) -> object:
        result_element = self.result_elements.get(dev_id, None)
        if result_element:
            return result_element.get()

        elem = self.acc.get(dev_id)
        return elem.peek(prop_id)

    async def set(self, dev_id: str, prop_id: str, value: object):
        # set state to changed
        with self.calculation_lock:
            self.model.changed()
            elem = self.acc.get(dev_id)
            r = await elem.update(property_id=prop_id, value=value)
        return r

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, acc={self.acc})"


    def _calculate_tune_if_required(self):
        with self.calculation_lock:
            if self.model.is_pending():
                self._calculate_tune()
            assert self.model.is_finished(), f"expected to be in finished state, but I am in {self.state.state}"

    def _calculate_tune(self):
        """
        This method is only  a helper method for _calculate_tune_if_required,
        It is not to be called when already running
        """
        logger.info("Calculating tune")
        assert self.model.is_pending(), f"expected to be in pending state, but I am in {self.state.state}"
        self.model.calculate()
        # Todo: implement calculation
        try:
            self.model.finished()
            tune = self.acc.get_tune()
        except Exception as exc:
            self.model.error()
            raise exc
        self.tune = tune
        logger.warning("Calculated tune to x=%.4f y=%.4f", self.tune.x, self.tune.y)

    def get_tune(self):
        self._calculate_tune_if_required()
        assert self.tune is not None, "expected some tune stored, but only found None"
        return self.tune



_all__ = ["SimulationBackend"]