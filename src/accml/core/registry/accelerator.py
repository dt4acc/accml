""" Module for the AO and registry functionality."""

from accml.core.config import AcceleratorConfig
from accml.core.registry.utils import WildcardDict

class Accelerator():

    def __init__(self, config: AcceleratorConfig):

        self._facility = config.facility
        self._machine = config.machine
        self._controls = config.controls
        self._simulators = config.simulators
        self._devices = WildcardDict(config.devices) # Dict which can use wildcards
        self._families = config.families


    @property
    def facility(self):
        return self._facility

    @property
    def machine(self):
        return self._machine

    @property
    def controls(self):
        if self._controls:
            return self._controls
        else:
            print('No controls have been configured.')

    @property
    def simulators(self):
        if self._simulators:
            return self._simulators
        else:
            print('No simulators have been configured.')

    @property
    def devices(self):
        if self._devices:
            return self._devices
        else:
            print('No devices have been configured.')

    @property
    def families(self):
        if self._families:
            return self._families
        else:
            print('No families have been configured.')

    def __str__(self):
        """Pretty printing of the accelerator configuration."""
        pass
