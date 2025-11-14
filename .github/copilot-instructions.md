# GitHub Copilot Instructions for accml

## Repository Overview

**accml** (Accelerator Control Middle Layer) is a Python package for operating and developing tools for high energy charged particle accelerators. It provides a control-system-agnostic interface that can be used by any facility.

### Key Features
- Get/set instrument attributes (magnet strengths, BPM positions)
- Facility-independent tuning tools
- Digital twin comparisons
- Flexible unit conversions
- Integration with EPICS and Tango control systems

## Project Structure

```
accml/
├── src/accml/
│   ├── core/              # Core abstractions and models
│   │   ├── model/         # Data models (identifiers, commands)
│   │   ├── bl/            # Business logic (conversions, liaison)
│   │   └── utils/         # Utilities (ophyd_async helpers)
│   ├── app/               # Applications (tune measurement, analysis)
│   └── custom/            # Facility-specific implementations
│       ├── bluesky/       # Bluesky measurement execution
│       └── facility_specific/
│           ├── bessyii/   # BESSY II EPICS implementation
│           └── bessyii_on_tango/  # BESSY II Tango implementation
├── tests/                 # Test files
├── examples/              # Example scripts
│   ├── tune/             # Tune measurement examples
│   └── device_checks/    # Device verification examples
└── docs/                  # Sphinx documentation
```

## Core Concepts

### Identifiers
- **LatticeElementPropertyID**: Identifies properties of lattice elements (magnets, BPMs)
- **DevicePropertyID**: Identifies properties of control system devices
- **ConversionID**: Maps between lattice and device properties

### Key Components
- **LiaisonManager**: Maps lattice elements to devices (forward/inverse lookups)
- **TranslatorManager**: Handles unit conversions between model and device values
- **YellowPages**: Directory of lattice elements
- **Bluesky Integration**: Uses Bluesky for measurement execution with databroker

## Development Workflow

### Installation
```bash
# Clone with submodules
git clone https://github.com/python-accelerator-middle-layer/accml.git
cd accml
git checkout dev/main
git submodule update --init --recursive

# Install in development mode
python3 -m pip install -e .
```

### Testing
```bash
# Run tests
python -m pytest tests/

# Run from outside source directory to test installed package
cd /tmp
python -m pytest /path/to/accml/tests
```

### Linting
```bash
# Check for syntax errors and undefined names
flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics

# Full lint with complexity checks
flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Building
```bash
# Build wheel
python -m pip wheel -w wheel/ ./

# Install wheel
python -m pip install wheel/accml-*.whl
```

## Code Style Conventions

### Python Standards
- **Python Version**: 3.9+ (tested on 3.9, 3.10, 3.11, 3.12)
- **Line Length**: Maximum 127 characters
- **Max Complexity**: 10
- **Linter**: flake8 with pycodestyle

### Design Patterns
- Use **dataclasses** with `frozen=True` for immutable identifiers
- Separate model definitions from business logic
- Factory pattern for setup functions (e.g., `setup()` in facility-specific modules)
- Manager pattern for lookups and conversions

### Imports
- Use absolute imports from `accml` package root
- Standard library first, then third-party, then local imports
- Group ophyd-async and control system imports together

## Testing Practices

### Test Structure
- Tests in `tests/` directory at repository root
- Use pytest framework
- Use fixtures for expensive setup (e.g., loading managers)
- Test data integrity, conversions, and consistency

### Key Test Areas
1. **Data Integrity**: Forward/inverse mapping consistency
2. **Conversions**: Unit conversion roundtrips
3. **Consistency**: YellowPages entries match LUT entries
4. **Completeness**: All mappings have conversions

### Example Test Pattern
```python
@pytest.fixture(scope="module")
def managers():
    """Load cached managers once."""
    yp, lm, tm = load_managers()
    return yp, lm, tm

def test_feature(managers):
    yp, lm, tm = managers
    # Test implementation
```

## Dependencies

### Core Dependencies
- **pydantic**: Data validation
- **jsons**: JSON serialization
- **databroker**: Data storage and retrieval
- **ophyd-async**: Async device control
- **aioca**: EPICS Channel Access async bindings
- **numpy**: Tested with both numpy<2.0 and numpy>=2.0

### Optional Dependencies
- **Bluesky**: Measurement execution engine
- Control system specific: EPICS or Tango

## Branch Strategy
- **dev/main**: Main development branch
- **epics/main**: EPICS-specific work
- **tango/main**: Tango-specific work

## CI/CD
- Tests run on Python 3.9, 3.10, 3.11, 3.12
- Tests run with numpy<2.0 and numpy>=2.0
- Linting with flake8
- Wheel building for distribution

## Important Notes

### Control System Agnostic Design
- Core functionality independent of control system
- Facility-specific implementations in `custom/facility_specific/`
- Abstract device interfaces to allow EPICS/Tango/other backends

### Unit Conversions
- Complex conversions between model units and device units
- Energy-dependent conversions supported
- Bidirectional (forward/inverse) conversions required

### Virtual Accelerator
- Development and testing use digital twin containers
- EPICS version: `apptainer run oras://registry.hzdr.de/digital-twins-for-accelerators/containers/pyat-softioc-digital-twin:v0-1-2-bessy.2475331`
- Tango version: (container to be specified)

## Common Tasks

### Adding a New Facility
1. Create directory in `src/accml/custom/facility_specific/{facility_name}/`
2. Implement `setup()` function returning configured devices
3. Create liaison translator setup with YellowPages, LiaisonManager, TranslatorManager
4. Define facility-specific constants

### Adding a Conversion
1. Create ConversionID with lattice and device property IDs
2. Implement conversion class (e.g., EnergyDependentLinearUnitConversion)
3. Add to TranslatorManager LUT
4. Test forward/inverse consistency

### Running Examples
```bash
# Start virtual accelerator first
apptainer run oras://...

# Run example (in another terminal)
cd examples/tune
python3 tune_response_measurement.py
```

## Documentation
- Sphinx-based documentation in `docs/`
- ReadTheDocs: https://pyaml.readthedocs.io/
- GitHub Pages: https://python-accelerator-middle-layer.github.io/pyaml/
- Software requirements: https://www.overleaf.com/read/hnrqzhfpbvpp

## Community
- **Mattermost**: https://mattermost.hzdr.de/accelerator-middle-layer/channels/town-square
- **Mailing List**: Contact S.Liuzzo to join
