import jsons

from accml.app.tune.model import Tune
from accml.core.interfaces.backend.backend import BackendR, BackendRW
from accml.core.interfaces.devices_facade import DevicesFacade


class OphydAsyncDeviceBackendR(BackendR):
    def __init__(self, *, devices: DevicesFacade):
        self.devices = devices

    def get_natural_view_name(self):
        return "device"

    async def trigger(self, dev_id: str, prop_id: str):
        raise NotImplementedError("needs to be done")

    async def read(self, dev_id: str, prop_id: str) -> object:
        dev = self.devices.get(dev_id)
        ch = getattr(dev, prop_id)
        r = await ch.read()
        # Todo: is it acceptable that only single data will arrive here?
        # Todo: remove this hack ... or use a dictionary
        #        instead of a data class
        if dev_id == "tune" and prop_id == "transversal":
            r = jsons.load(r["tune-transversal"]["value"], Tune)
        return r
        raise NotImplementedError("needs to be done")


class OphydAsyncDeviceBackendRW(OphydAsyncDeviceBackendR, BackendRW):
    def __init__(self, *, devices: DevicesFacade):
        super().__init__(devices=devices)

    async def set(self, dev_id: str, prop_id: str, value: object):
        dev = self.devices.get(dev_id)
        ch = getattr(dev, prop_id)
        r = await ch.set(value)
        return r
