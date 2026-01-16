# KRV CAN Bus Engine
### K.R.Engineers Internal TOOL<br>Navneet Singh

A powerful CAN bus monitoring and logging tool designed to capture, parse, and analyze CAN bus traffic using DBC (Database Container) files.

## Overview

The KRV CAN Bus Engine is a software tool that enables real-time monitoring and logging of CAN bus communications. It parses CAN messages according to DBC file specifications and generates structured log files for analysis.
## Index

- [Overview](#overview)
- [Features](#features)
- [Future Enhancements](#future-enhancements)
- [Usage](#usage)
- [System Architecture](#system-architecture)



## Features

- **DBC File Support**: Parse CAN messages using industry-standard DBC files
- **Network Connectivity**: Connect to CAN bus via IP port
- **Logging Capabilities**: Generate structured output logs in specified directories
- **Configurable Runtime**: Control execution duration by time or frame count
- **Future GUI/TUI**: Planned graphical and terminal user interfaces for real-time data visualization

### Future Enhancements

- **TUI/GUI Interface**: Interactive terminal or graphical user interface to display real-time parsed CAN bus data
- Real-time data visualization and monitoring
- Signal filtering and search capabilities
- Export functionality for various data formats

- Have the ability to construct database from a list of '.dbc' files.


## Usage

```bash
# Example usage (to be updated with actual command syntax)
python krv_can_engine.py \
    --dbc <path_to_dbc_file> \
    --port <can_ip_port> \
    --output <output_directory> 
```

## Contributing

This project is under active development. Contributions and suggestions are welcome.

---

**Note**: This README will be updated as the project evolves and additional features are implemented.


## System Architecture

### Architecture Diagram

### Data Flow

```
┌─────────────┐
│   User      │
│   Input     │
└──────┬──────┘
       │
       │ python3 main.py --dbc file.dbc --port can0 --output ./logs
       ▼
┌─────────────────────┐
│   Argument Parser   │  Validates inputs, creates directories
└──────────┬──────────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
┌──────────────────┐  ┌──────────────────┐
│  KRV_Logger      │  │  KRV_CanEngine   │
│  Initialized     │  │  Initialized     │
└──────────────────┘  └────────┬─────────┘
                               │
                ┌──────────────┴───────────────┐
                │                              │
                ▼                              ▼
    ┌───────────────────────┐      ┌───────────────────────┐
    │  Load DBC File        │      │  Connect to CAN Bus   │
    │  • Parse messages     │      │  • Open socketcan     │
    │  • Parse signals      │      │  • Set timeout        │
    └───────────┬───────────┘      └───────────┬───────────┘
                │                              │
                └──────────────┬───────────────┘
                               │
                               ▼
                    ┌───────────────────────┐
                    │   Main Loop           │
                    │   while True:         │
                    │     msg = next()      │
                    └───────────┬───────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
    ┌───────────────────────┐      ┌───────────────────────┐
    │  Receive CAN Message  │      │  Decode with DBC      │
    │  • ID, DLC, Data      │      │  • Match message ID   │
    │                       │      │  • Extract signals    │
    └───────────┬───────────┘      └───────────┬───────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Log to File         │
                    │   • Timestamp         │
                    │   • Decoded data      │
                    └───────────────────────┘
```

