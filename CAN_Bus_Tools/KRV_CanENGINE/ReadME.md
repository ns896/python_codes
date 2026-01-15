# KRV CAN Bus Engine
### K.R.Engineers Internal TOOL<br>Navneet Singh

A powerful CAN bus monitoring and logging tool designed to capture, parse, and analyze CAN bus traffic using DBC (Database Container) files.

## Overview

The KRV CAN Bus Engine is a software tool that enables real-time monitoring and logging of CAN bus communications. It parses CAN messages according to DBC file specifications and generates structured log files for analysis.
## Index

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
  - [Basic Requirements](#basic-requirements)
  - [Future Enhancements](#future-enhancements)
- [Usage](#usage)



## Features

- **DBC File Support**: Parse CAN messages using industry-standard DBC files
- **Network Connectivity**: Connect to CAN bus via IP port
- **Logging Capabilities**: Generate structured output logs in specified directories
- **Configurable Runtime**: Control execution duration by time or frame count
- **Future GUI/TUI**: Planned graphical and terminal user interfaces for real-time data visualization

## Requirements

### Basic Requirements

The tool requires the following inputs:

1. **DBC File Input**
   - Command-line argument to specify the DBC (Database Container) file path

2. **CAN IP Port**
   - Command-line argument to specify the CAN bus IP port/address

3. **Output Directory**
   - Argument to specify the directory where log files will be generated
   - Logs are saved in a structured format for easy analysis

4. **Runtime Control**
   - Option to specify execution duration:
     - Time-based: Run for a specified duration (e.g., 60 seconds)
     - Frame-based: Process a specific number of CAN frames

### Future Enhancements

- **TUI/GUI Interface**: Interactive terminal or graphical user interface to display real-time parsed CAN bus data
- Real-time data visualization and monitoring
- Signal filtering and search capabilities
- Export functionality for various data formats

## Usage

```bash
# Example usage (to be updated with actual command syntax)
python krv_can_engine.py \
    --dbc <path_to_dbc_file> \
    --port <can_ip_port> \
    --output <output_directory> \
    --duration <time_in_seconds> \
    --frames <number_of_frames>
```

## Project Structure

```
KRV_CanENGINE/
├── ReadME.md          # This file
└── [source files]     # Implementation files
```

## Contributing

This project is under active development. Contributions and suggestions are welcome.

---

**Note**: This README will be updated as the project evolves and additional features are implemented.
