[![Documentation Status](https://readthedocs.org/projects/pyaml/badge/?version=latest)](https://pyaml.readthedocs.io/en/latest/?badge=latest)

# pyAML: python accelerator middle layer

disclaimer: the pyAML software is still under conception and development

pyAML is a sofware meant to operate and develop new tools for high energy charged particle accelerators. 
pyAML it will be control agnostics and can be used by any facility
pyAML it will allow easy scripting as for MML

The pyAML documentation can be fund [here](https://pyaml.readthedocs.io/en/latest/) [and here](https://python-accelerator-middle-layer.github.io/pyaml/)


This repository contains the Python Accelerator Middle Layer (pyAML).

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
### 4. Run the Virtual Accelerator (Test bench)
```bash 
apptainer run oras://registry.hzdr.de/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin:v0-2-5.2314849
```
Keep this terminal running — it simulates a virtual accelerator backend.
### 5. Run the pyAML Client (example)
```bash
cd examples/tune
python3 tune.py


    
