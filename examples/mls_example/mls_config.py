"""Example to create configuration for MLS using config classes."""

from accml.core.config import AcceleratorConfig, EPICSConfig, SimulatorConfig, MagnetConfig, EPICSType
from accml.core.registry.utils import WildcardDict

#%% Facility and machine name
facility = 'MLS'
machine = 'storage_ring'

#%% Control system modes
live = EPICSConfig(access_type=EPICSType.CA)
twin = EPICSConfig(access_type=EPICSType.CA,pv_prefix='twin')

#%% Simulator modes
design = SimulatorConfig(type='pyat',model='design_lattice.json')
error = SimulatorConfig(type='pyat',model='error_lattice.json')
measured = SimulatorConfig(type='pyat',model='measured_lattice.json')

#%% Devices

# Quadrupoles
quads = []
families = ['Q1','Q2','Q3']
cells = ['1','2']
sections = ['K1','L2','K3','L4']

for quad in families:
    for cell in cells:
        for section in sections:
            quads.append(MagnetConfig(name=f'{quad}M{cell}{section}RP',type='quadrupole',power_supply=f'{quad}P{cell}{section}RP'))

# Generate a dictionary of the quadrupole configurations
quads_by_name = {q.name: q for q in quads}

#%% Families

Q1 = [device.name for device in WildcardDict(quads_by_name)['Q1*']]
Q2 = [device.name for device in WildcardDict(quads_by_name)['Q2*']]
Q3 = [device.name for device in WildcardDict(quads_by_name)['Q3*']]
TuneCorrectors = Q1 + Q3

families = {'Q1': Q1,
            'Q2': Q2,
            'Q3': Q3,
            'TuneCorrectors': TuneCorrectors}

#%% Accelerator

config = AcceleratorConfig(facility=facility, machine=machine,
                           controls = {'live': live, 'twin': twin},
                           simulators = {'design': design,
                                         'error': error,
                                         'measured': measured
                                         },
                           devices = quads_by_name,
                           families = families
                           )