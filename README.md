[![Documentation](https://github.com/python-accelerator-middle-layer/accml/actions/workflows/docs.yml/badge.svg)](https://python-accelerator-middle-layer.github.io/accml/)

# accml: Accelerator middle layer

`accml` is a software stack designed to facilitate implementing tools 
 characterising (high) energy charged accelerator.

These tools typically address:
* characterising an accelerator
* commissioning of an accelerator
* forecasting the performance of an accelerator, which is currently under design.

For details of its concept see [design.md](https://github.com/python-accelerator-middle-layer/accml/design.md).


## 🚀 Installation and Running Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/python-accelerator-middle-layer/accml.git
cd accml

### 2. Install Dependencies
```bash  
git checkout dev/main

git submodule update --init --recursive
```
### 3. Install the Package

Please note: accml is not **per se** depending on bluesky.
It does use *ophyd_async* for communicating to EPICS or TANGO.

ophyd_async imports python protocol definitions from bluesky.
We are confident that this dependency can be dropped at a later
stage.

### 3.1 EPICS facility
```bash
python3 -m pip install \
   -e ./external-repositories/accml_lib/[bluesky-epics,pyat-simulator] \
   -e ./[bluesky-epics]
```

### 3.2 TANGO facility
```bash
python3 -m pip install \
   -e ./external-repositories/accml_lib/[bluesky-tango,pyat-simulator] \
   -e ./[bluesky-tango]
```


### 4. Run the Virtual Accelerator (Test bench) --EPICS VERSION
```bash 
apptainer run oras://registry.hzdr.de/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin:v0-1-2-bessy.2475331

apptainer run oras://registry.hzdr.de/digital-twins-for-accelerators/epics-tools:latest
```
Keep this terminal running — it simulates a virtual accelerator backend.
### 5. Run the pyAML Client (example)
```bash
cd examples/10_epics/02_bluesky/accml_interface
python3 01_tune_response_measurement.py
```

### 4.1 Run the Virtual Accelerator (Test bench) --TANGO VERSION
## 4.1.1 Assuming mysql is runnig. or run below my sql container

```bash
apptainer pull -F virtual-accelerator.sif oras://gitlab-registry.synchrotron-soleil.fr/software-control-system/containers/apptainer/virtual-accelerator:latest
apptainer run --cleanenv virtual-accelerator.sif
```
Keep this terminal running — it simulates a virtual accelerator backend.
### 5.1 Run the pyAML Client (example)
```bash
cd examples/20_epics/02_bluesky/accml_interface
```

execute:
```bash
python3 01_tune_response_measurement.py
```
    
