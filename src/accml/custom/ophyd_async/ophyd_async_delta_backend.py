"""

Delta Backend when measuring with ophyd-async

Todo:
    implement it as filters passed to :class:`DeltaBackendRProxy` or
    :class:`DeltaBackendRWProxy`

    Following acquire instead of inherit
"""
from typing import Dict

from bluesky.protocols import Reading

from accml_lib.core.bl.delta_backend import DeltaBackendRProxy, DeltaBackendRWProxy, StateCache, delta_property
from accml_lib.core.interfaces.backend.backend import BackendR, BackendRW
from accml_lib.core.interfaces.backend.filter import FilterInterface, T


class ExtractSingleValue(FilterInterface):

    def process(self, input: Dict[str, Dict[str, Reading]]) -> T:
        key, = list(input)
        return input[key]["value"]


class OphydAsyncDeltaBackendRProxy(DeltaBackendRProxy):
    def __init__(self, *, backend: BackendR, cache: StateCache, filter: FilterInterface=ExtractSingleValue()):
        super().__init__(backend=backend, cache=cache, filter=filter)
    # def _calculate_delta_read(self, rcmd: ReadCommand, value):
    #     ref = self.cache.get(rcmd, None)
    #     assert ref is not None
    #    key, = list(ref.keys())
    #     datum = ref[key]
    #     r = value - datum["value"]
    #    return r


class OphydAsyncDeltaBackendRWProxy(OphydAsyncDeltaBackendRProxy, DeltaBackendRWProxy):
    def __init__(self, *, backend: BackendRW, cache: StateCache, filter: FilterInterface=ExtractSingleValue()):
        super().__init__(backend=backend, cache=cache, filter=filter)

    # def _calculate_delta_set(self, rcmd: ReadCommand, value):
    #     ref = self.cache.get(rcmd, None)
    #     assert ref is not None
    #     # only prepared currently that a single value was stored
    #    key, = list(ref.keys())
    #    datum = ref[key]
    #    r =  value + datum["value"]
    #    return r
