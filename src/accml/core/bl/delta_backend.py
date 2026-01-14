import logging

from ..interfaces.backend.backend import BackendRW, BackendR
from ..model.command import ReadCommand

logger = logging.getLogger("accml")


class StateCache:
    """
    Todo:
        abstract interface
    """

    def __init__(self, *, name: str):
        self.cache = dict()
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def clear(self):
        self.cache = dict()

    def get(self, id, default=None):
        """
        Todo:
            add return type: shall support __sub__
        """
        assert self.cache is not None
        return self.cache.get(id, default)

    def set(self, id, value):
        assert self.cache is not None
        self.cache[id] = value


def delta_property(prop_id: str) -> (bool, str):
    if prop_id[:6] == "delta_":
        return True, prop_id[6:]
    return False, prop_id


class DeltaBackendRProxy(BackendR):
    """handle delta properties"""

    def __init__(self, *, backend: BackendR, cache: StateCache):
        self.backend = backend
        self.cache = cache

    def __repr__(self):
        return f"{self.__class__.__name__}(backend={self.backend}, cache={self.cache})"

    def get_natural_view_name(self):
        return self.backend.get_natural_view_name()

    async def trigger(self, dev_id: str, prop_id: str):
        flag, orig_prop_id = delta_property(prop_id)
        if not flag:
            return await self.backend.trigger(dev_id=dev_id, prop_id=prop_id)
        return await self.backend.trigger(dev_id=dev_id, prop_id=orig_prop_id)

    async def read(self, dev_id: str, prop_id: str) -> object:
        flag, orig_prop_id = delta_property(prop_id)
        if not flag:
            return await self.backend.read(dev_id=dev_id, prop_id=prop_id)
        r = await self.backend.read(dev_id=dev_id, prop_id=orig_prop_id)
        rcmd = ReadCommand(id=dev_id, property=prop_id)
        ref = self.cache.get(rcmd, None)
        if ref is None:
            rcmd = ReadCommand(id=dev_id, property=prop_id)
            self.cache.set(rcmd, r)
        # to get some zero of proper type
        return self._calculate_delta_read(rcmd, r)

    def _calculate_delta_read(self, rcmd: ReadCommand, value):
        """
        For overloading in derived classes e.g. for processing ophyd-async data
        """
        ref = self.cache.get(rcmd, None)
        assert ref is not None
        return value - ref


class DeltaBackendRWProxy(DeltaBackendRProxy, BackendRW):
    """handle delta properties"""

    def __init__(self, backend: BackendRW, cache: StateCache):
        super().__init__(backend=backend, cache=cache)
        self.backend = backend

    async def set(self, dev_id: str, prop_id: str, value: object):
        flag, orig_prop_id = delta_property(prop_id)
        if not flag:
            return await self.backend.set(dev_id=dev_id, prop_id=prop_id, value=value)

        rcmd = ReadCommand(id=dev_id, property=prop_id)
        ref = self.cache.get(rcmd, None)
        if not ref:
            r = await self.backend.read(dev_id=dev_id, prop_id=orig_prop_id)
            # Todo: refactor the classes here so this does not need
            #        to be repeated here
            self.cache.set(rcmd, r)
        total_val = self._calculate_delta_set(rcmd, value)
        return await self.backend.set(
            dev_id=dev_id, prop_id=orig_prop_id, value=total_val
        )

    def _calculate_delta_set(self, rcmd: ReadCommand, value):
        """
        For overloading in derived classes e.g. for processing ophyd-async data
        """
        ref = self.cache.get(rcmd, None)
        assert ref is not None
        return value + ref
