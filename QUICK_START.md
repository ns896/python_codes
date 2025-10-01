# Quick Start Guide

## Install Your Packages

```bash
# Navigate to your project
cd /home/nsingh/python_codes

# Install in editable mode (recommended)
pip install -e .

# Or install with specific features
pip install -e ".[can-tools]"  # With CAN bus tools
pip install -e ".[dev]"        # With development tools
```

## Test Installation

```bash
# Run the test script
python test_installation.py
```

## Use Your Libraries

### In Python Scripts

```python
# Import your custom libraries
from krv_logger import KRV_Logger
from krv_comman.TUI import BasicTUI
from AC_Measurement_System import read_pzem_016_data
from CAN_Bus_Tools import MobilEyeVisualizer

# Use them
logger = KRV_Logger("my_app", "app.log", "INFO")
log = logger.get_logger()
log.info("Hello from my custom logger!")
```

### Command Line Tools

```bash
# AC Measurement System
ac-measurement

# CAN Bus Parser  
can-parser

# CAN Data Visualizer
can-visualizer

# KRV Logger Test
krv-logger-test
```

## Key Benefits

✅ **Install anywhere**: Use `pip install -e .` to install your packages  
✅ **Import anywhere**: Import your libraries in any Python script  
✅ **Command line tools**: Access your tools from terminal  
✅ **Dependency management**: Automatic installation of required packages  
✅ **Editable install**: Changes to code are immediately available  

## Next Steps

1. **Test**: Run `python test_installation.py`
2. **Use**: Import your libraries in other projects
3. **Extend**: Add new packages to `pyproject.toml`
4. **Share**: Others can install with `pip install -e .`

Your custom libraries are now ready to use anywhere!
