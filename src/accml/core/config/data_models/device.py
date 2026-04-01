""" Configuration classes for devices."""

from pydantic import BaseModel, Field
from abc import ABC
from typing import Hashable, Optional
from .conversions import ConversionConfig

# TODO: figure out what is required for a device and what is same/different
# depending on the control system
# It needs to also be possible to configure devices from external modules
# in the same way.

class DeviceConfig(BaseModel, ABC):
    name: Hashable # e.g., 'QF1C01A'
    # TODO: what is common for all devices?


class MagnetConfig(DeviceConfig):
    magnet_type: str = Field(alias="type")
    device_id: Optional[Hashable] = None# Engineering id, can be used for example to
    # link to specific excitation curve or magnet model.
    power_supply: Optional[Hashable] = None
    conversion: Optional[ConversionConfig] = None


# class ResponseModel(BaseModel):
#     """General response model for a device reacting to a control input change

#     Timeout: whithin this time the device has to answer
#     Settle time: after this time the device is expected to be in a stable state
#     """

#     #: seconds
#     timeout: float
#     # seconds
#     settle_time: float


# class PowerConverterInterface(BaseModel):
#     #:  e.g., 'CHANNEL:QF1C01A:SP'
#     setpoint: str
#     #: e.g., 'CHANNEL:QF1C01A:RB'
#     readback: str


# class PowerConverter(BaseModel):
#     id: Hashable
#     interface: PowerConverterInterface
#     response: ResponseModel

#     def get_current(self):
#         return 0.0