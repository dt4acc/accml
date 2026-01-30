"""

For those that don't want to use a measurement execution engine
based on bluesky (measurement orchestration) software stack

"""
from accml_lib.core.bl.delta_backend import DeltaBackendRProxy, DeltaBackendRWProxy
from accml_lib.core.model.utils.command import ReadCommand


class OphydAsyncDeltaBackendRProxy(DeltaBackendRProxy):
    def _calculate_delta_read(self, rcmd: ReadCommand, value):
        ref = self.cache.get(rcmd, None)
        assert ref is not None
        key, = list(ref.keys())
        datum = ref[key]
        r = value - datum["value"]
        return r


class OphydAsyncDeltaBackendRWProxy(OphydAsyncDeltaBackendRProxy, DeltaBackendRWProxy):
    def _calculate_delta_set(self, rcmd: ReadCommand, value):
        ref = self.cache.get(rcmd, None)
        assert ref is not None
        # only prepared currently that a single value was stored
        key, = list(ref.keys())
        datum = ref[key]
        r =  value + datum["value"]
        return r
