"""Example how to use registry for MLS."""

from mls_config import config
from accml.core.registry.accelerator import Accelerator


#%% Create the accelerator object

mls = Accelerator(config)

#%% Extract information from the registry

print(f'Facility: {mls.facility}\n')
print(f'Machine: {mls.machine}\n')
print(f'Controls: {mls.controls}\n')
print(f'Simulators: {mls.simulators}\n')
print(f'Devices: {mls.devices}\n')
print(f'Families: {mls.families}\n')