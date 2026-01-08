import logging
import threading

from transitions import Machine

from accml.core.interfaces.backend.backend import BackendRW
from ..interface.accelerator_simulator import AcceleratorSimulatorInterface
from ..interface.result_element import ResultElement
from ..model.calculation_states import CalculationStates as States
from accml.app.tune.model import Tune

logger = logging.getLogger()

# class OrbitElement
# needs to be implemented
#    pass

# class TwissElement(ResultElement):
#     def __init__(self, backend):
#        self.backend = backend
#
#    def get(self, prop_id: str) -> Tune:


class TuneElement(ResultElement):
    def __init__(self, backend):
        self.backend = backend

    def get(self, prop_id: str) -> Tune:
        assert prop_id == "transversal", "Only prepared to handle transveral tune"
        return self.backend.get_tune()


class SimulationStateModel:
    """all methods added by class::`transitions.Machine`

    transititions used as bluesky seems not to use
    superstate machine any more
    """


class SimulatorBackend(BackendRW):
    """
    Todo:
        where to break async / sync or threaded approach?

    I assume today that the calculation engine works the following way:

    1. set to a state
    2. then calculations are triggered

    So the calculations shall only happen after the state was
    set (completely).This is not (and can not) directly observed
    here. Here the calculation is only conducted when its results
    are requested. Calculation, setting, and  reading back
    calculation results are protected by a lock, so no more sets
    are made while calculation is running nor calculation results
    are delivered ahead of time.
    """

    def __init__(self, *, acc: AcceleratorSimulatorInterface, name: str, logger=logger):
        self.acc = acc
        self.logger = logger
        self.name = name

        self.tune = None

        # While calculation is running
        # * don't allow setting data
        # * don't provide calculation results:  Twiss, tune, orbit
        #
        # Todo: should reads also be protected (by a Read / Write Lock)
        #       should the lock be an asyncio lock?
        self.calculation_lock = threading.Lock()
        self.model = SimulationStateModel()
        self.state = Machine(
            model=self.model,
            # fmt:off
            transitions=[
                dict( trigger = "calculate" , source = States.pending   , dest = States.executing , before=self._clear_stored_results ),
                dict( trigger = "finished"  , source = States.executing , dest = States.finished                                      ),
                dict( trigger = "changed"   , source = States.finished  , dest = States.pending   , after=self._clear_stored_results  ),
                dict( trigger = "changed"   , source = States.pending   , dest = States.pending   , after=self._clear_stored_results  ),
                dict( trigger = "clear"     , source = States.error     , dest = States.pending                                       ),
                dict( trigger = "error"     , source = "*"              , dest = States.error                                         ),
            ],
            # fmt:on
            states=[st for st in States],
            initial=States.pending,
        )

        self.result_elements = dict(
            # twiss=TwissElement(backend=self),
            tune=TuneElement(backend=self)
        )

    def _clear_stored_results(self):
        self.tune = None

    def get_natural_view_name(self):
        return "design"

    async def trigger(self, dev_id: str, prop_id: str):
        self.logger.info(
            "%s(name=%s) no trigger needed", self.__class__.__name__, self.name
        )

    async def read(self, dev_id: str, prop_id: str) -> object:
        """

        Todo:
            acquire lock for read too? So that no inconsistent
            state will be read?
        """
        result_element = self.result_elements.get(dev_id, None)
        if result_element:
            return result_element.get(prop_id)

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

    def get_tune(self):
        self._calculate_tune_if_required()
        assert self.tune is not None, "expected some tune stored, but only found None"
        return self.tune

    def _calculate_tune_if_required(self):
        with self.calculation_lock:
            if self.model.is_pending():
                self._calculate_tune()
            assert (
                self.model.is_finished()
            ), f"expected to be in finished state, but I am in {self.model.state}"

    def _calculate_tune(self):
        """
        This method is only  a helper method for _calculate_tune_if_required,
        It is not to be called when already running
        """
        logger.debug("Calculating tune")
        assert (
            self.model.is_pending()
        ), f"expected to be in pending state, but I am in {self.model.state}"
        self.model.calculate()
        try:
            tune = self.acc.get_tune()
            self.model.finished()
        except Exception as exc:
            self.model.error()
            raise exc
        self.tune = tune
        logger.info("Calculated tune to x=%.4f y=%.4f", self.tune.x, self.tune.y)


_all__ = ["SimulationBackend"]
