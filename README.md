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
```bash
python3 -m pip install -e .
```
### 4. Run the Virtual Accelerator (Test bench) --EPICS VERSION
```bash 
apptainer run oras://registry.hzdr.de/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin:v0-1-2-bessy.2475331
```
Keep this terminal running — it simulates a virtual accelerator backend.
### 5. Run the pyAML Client (example)
```bash
cd examples/tune
python3 tune_response_measurement.py
```

### 4.1 Run the Virtual Accelerator (Test bench) --TANGO VERSION
## 4.1.1 Assuming mysql is runnig. or run below my sql container
```bash
where is mysql container
```

```bash
apptainer run oras://registry.hzdr.de/digital-twins-for-accelerators/containers/pyat-tango-digital-twin:v0-1-0.2554955
```
Keep this terminal running — it simulates a virtual accelerator backend.
### 5.1 Run the pyAML Client (example)
```bash
cd examples/tune
```
Comment line 14 and uncomment line 15 in tune_response_measurement.py. Then  it should look like this:

```python3

# from accml.custom.accml_lib.bessyii.setup import setup
from accml.custom.accml_lib.bessyii_on_tango.setup import setup

```
Now you can execute on the command line:

execute:
```bash
python3 tune_response_measurement.py
```
    
