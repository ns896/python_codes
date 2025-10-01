# Installation Guide

This guide explains how to install and use your custom Python libraries using `pyproject.toml`.

## What is pyproject.toml?

`pyproject.toml` is the modern standard for Python package configuration. It allows you to:

- **Define packages**: Tell Python what code to include
- **Specify dependencies**: What other packages your code needs  
- **Create entry points**: Command-line tools and scripts
- **Configure build tools**: How to build and install your package
- **Make packages installable**: Install anywhere with `pip install`

## Package Structure

Your project is organized as follows:

```
python_codes/
├── pyproject.toml          # Package configuration
├── krv_logger/            # Custom logging library
│   ├── __init__.py
│   └── krv_logger.py
├── krv_comman/            # Common utilities
│   ├── __init__.py
│   └── TUI/
│       ├── __init__.py
│       └── basic_tui.py
├── AC_Measurement_System/ # AC measurement tools
│   ├── __init__.py
│   ├── main.py
│   └── assets/
└── CAN_Bus_Tools/         # CAN bus analysis tools
    ├── __init__.py
    ├── CAN_BUS_Parser.py
    ├── MobilEye_DataVisualizer.py
    └── dbc_files/
```

## Installation Methods

### 1. Editable Install (Recommended for Development)

This installs your package in "editable" mode, so changes to your code are immediately available:

```bash
# Navigate to your project directory
cd /home/nsingh/python_codes

# Install in editable mode
pip install -e .

# Or with specific dependencies
pip install -e ".[can-tools]"  # With CAN bus tools
pip install -e ".[dev]"        # With development tools
pip install -e ".[all]"        # With all dependencies
```

### 2. User Install

Installs to your user directory (no sudo required):

```bash
pip install --user .
```

### 3. System Install

Installs system-wide (requires sudo):

```bash
sudo pip install .
```

### 4. Virtual Environment (Recommended)

Create a clean environment for your project:

```bash
# Create virtual environment
python3 -m venv my_project_env

# Activate it
source my_project_env/bin/activate

# Install your package
pip install -e .

# Deactivate when done
deactivate
```

## Using Your Libraries

After installation, you can import and use your libraries anywhere:

### Python Scripts

```python
# Import your custom libraries
from krv_logger import KRV_Logger
from krv_comman.TUI import BasicTUI
from AC_Measurement_System import ACMeasurementTUI, read_pzem_016_data
from CAN_Bus_Tools import MobilEyeVisualizer

# Use them
logger = KRV_Logger("my_app", "app.log", "INFO")
log = logger.get_logger()
log.info("Hello from my custom logger!")

# Use AC measurement
data = read_pzem_016_data()
print(f"Voltage: {data['voltage_V']}V")

# Use CAN visualizer
visualizer = MobilEyeVisualizer()
```

### Command Line Tools

After installation, these commands become available:

```bash
# AC Measurement System TUI
ac-measurement

# CAN Bus Parser
can-parser

# CAN Data Visualizer
can-visualizer

# KRV Logger Test
krv-logger-test
```

## Dependency Management

### Core Dependencies (Always Installed)
- `pyserial>=3.5` - Serial communication
- `minimalmodbus>=2.1.1` - Modbus communication

### Optional Dependencies

Install specific feature sets:

```bash
# CAN Bus Tools
pip install -e ".[can-tools]"

# AC Measurement
pip install -e ".[ac-measurement]"

# Visualization tools
pip install -e ".[visualization]"

# Development tools
pip install -e ".[dev]"

# Everything
pip install -e ".[all]"
```

## Development Workflow

### 1. Make Changes
Edit your Python files in the project directory.

### 2. Test Changes
If using editable install, changes are immediately available:

```python
# In any Python script
from krv_logger import KRV_Logger  # Uses latest version
```

### 3. Update Dependencies
If you add new dependencies, update `pyproject.toml`:

```toml
dependencies = [
    "pyserial>=3.5",
    "minimalmodbus>=2.1.1",
    "new-package>=1.0.0",  # Add new dependency
]
```

Then reinstall:
```bash
pip install -e .
```

## Troubleshooting

### Import Errors
If you get import errors:

1. Make sure the package is installed:
   ```bash
   pip list | grep python-codes
   ```

2. Check if you're in the right environment:
   ```bash
   which python
   pip show python-codes
   ```

### Permission Errors
If you get permission errors, use user install:
```bash
pip install --user -e .
```

### Virtual Environment Issues
Make sure you're in the right environment:
```bash
# Check current environment
echo $VIRTUAL_ENV

# Activate if needed
source your_env/bin/activate
```

## Advanced Usage

### Building Distribution Packages

Create installable packages:

```bash
# Build wheel
python -m build

# Install from wheel
pip install dist/python_codes-0.1.0-py3-none-any.whl
```

### Publishing to PyPI

To share your package with others:

1. Create accounts on [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
2. Build and upload:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

3. Others can install with:
   ```bash
   pip install python-codes
   ```

## Next Steps

1. **Test your installation**: Try importing your libraries
2. **Create more packages**: Add new functionality
3. **Add tests**: Create test files in a `tests/` directory
4. **Documentation**: Add docstrings and create documentation
5. **Version control**: Use git to track changes

Your packages are now ready to use anywhere Python is installed!
