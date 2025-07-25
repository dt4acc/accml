"""A collection of power converters exported as if these were multiplexed

Todo:
    Review if the multiplex itself should be contained in this file too
    Or a helper function to generate it ...
"""
import asyncio
import logging
import time
from typing import Dict, Union, Sequence

from bluesky.protocols import Movable, Stageable, Reading
from event_model import DataKey
from ophyd_async.core import StandardReadable, soft_signal_rw, StandardReadableFormat as Format, LazyMock, \
    DEFAULT_TIMEOUT

logger = logging.getLogger("accml")


def rename_dict_keys(
    d: Dict[str, Reading], src_prefix: str, tgt_prefix: str
) -> Dict[str, Reading]:
    logger.debug('Renaming prefix from "%s" to "%s"', src_prefix, tgt_prefix)

    def rename_key(key):
        tmp, r = key.split(src_prefix)
        assert tmp == ""
        new_key = tgt_prefix + r
        return new_key

    return {rename_key(key): item for key, item in d.items()}


class _ProxiedDeviceName(StandardReadable, Movable, Stageable):
    """A capsule storing the name of the currently selected device

    Expected to be used together with _MultiplexerItemProxy
    """

    def __init__(
        self,
        *,
        name: str,
        default_name: str = "Unknown",
        acceptable_names: Sequence[str],
    ):
        self.proxied_name = default_name
        self.acceptable_names = acceptable_names
        self.timestamp = time.time()

        super().__init__(name=name)
        assert self.proxied_name is not None


    async def describe(self) -> dict[str, DataKey]:
        return {
            f"{self.name}-proxied_name": DataKey(source="", dtype="string", shape=[])
        }

    async def read(self) -> dict[str, Reading]:
        return {
            f"{self.name}-proxied_name": Reading(
                value=self.proxied_name, timestamp=self.timestamp
            )
        }

    async def set(self, name: str):
        self.timestamp = time.time()
        assert name in self.acceptable_names
        self.proxied_name = name
        # return Status(success=True, done=True)

    def get_name(self) -> str:
        return self.proxied_name


class _MultiplexerItemProxy(StandardReadable, Movable,  Stageable):
    def __init__(
        self,
        *args,
        name: str = "",
        settable_devices: Dict[str, Union[Movable, StandardReadable, Stageable]],
        **kwargs,
    ):
        self.settable_devices = settable_devices
        super().__init__(name=name)


    @property
    def _proxied_dev_name(self):
        return self.parent.sel.get_name()

    @property
    def _proxied_device(self) -> Union[Movable, StandardReadable, Stageable]:
        return self.settable_devices[self._proxied_dev_name]

    def _rename_keys(self, d):
        return rename_dict_keys(d, self._proxied_device.name, self.name)

    async def describe_configuration(self):
        d = await super().describe_configuration()
        d.update(self._rename_keys(d))
        return d

    async def read_configuration(self):
        d = await super().read_configuration()
        d.update(self._rename_keys(d))
        return d

    async def describe(self):
        d = await super().describe()
        d.update(self._rename_keys(d))
        return d

    async def read(self):
        """return data for the proxied device
        """
        stat1 = super().read()
        stat2 =  self._proxied_device.read()
        d = await stat1
        proxied_data = await stat2
        return self._rename_keys(proxied_data)

    async def set(self, val):
        """
        Todo:
            check how
        """
        return self._proxied_device.set(val)

    async def stop(self):
        pass

class MultiplexerProxy(StandardReadable, Stageable):
    """
    Todo:
        check which other functions need to be overloaded

        is the functionallity required that the user can request
        that all settable devices are added in the output?

        Or would it be better to instruct the user to take care of it
        themselves? Just add them to the list of detectors to the
        RunEngine
    """
    def __init__(
        self,
        *args,
        name: str = "",
        settable_devices: Dict[str, Union[Movable, StandardReadable, Stageable]],
        default_name: str = "",
        ItemProxy=_MultiplexerItemProxy,
        **kwargs,
    ):
        with self.add_children_as_readables():
            # referenced here to be accessible
            self.sel = _ProxiedDeviceName(
                name=f"{name:}-sel",
                default_name=default_name,
                acceptable_names=list(settable_devices.keys()),
            )
            self.proxy = ItemProxy(
                name=f"{name:}-proxy",  settable_devices=settable_devices
            )
            self.settable_devices = settable_devices
        super().__init__(*args, **kwargs)
        assert self.proxy._proxied_dev_name is not None

    async def stop(self, success=False):
        return await self.proxy.stop()

    async def connect(self, *args, **kwargs) -> None:
        """
        Todo:
            can I return all stats directly?
            learn how this is correctly done
        """
        stat =  super().connect(*args, **kwargs)
        stats = asyncio.gather(
            *[pc.connect(*args, **kwargs) for _, pc in self.settable_devices.items()],
            # return_exceptions=True,
        )
        rall = await stats
        r =  await stat
        return r

__all__ = ["MultiplexerProxy"]
