# CAN Bus Tools

This repository contains tools for replaying CAN data from recorded log files.

## Table of Contents
- [Mobil Eye Visualizer](#mobil-eye-visualizer)
- [Canplayer](#canplayer) 
- Set Up Virtual CAN Port
  - [Virtual CAN Setup](#virtual-can-setup)
    - [Prerequisites](#require-modules)
    - [Create Virtual CAN Interface](#create-virtual-can-interface)
- Python Virtual Environment
  - [PyEnv Setup](#pyenv-setup)
  - [Installation](#installation)
  - [Usage](#usage)

## Mobil Eye Visualizer

Steps to get the Mobil Eye Data Visualizer 

Step 1 - Run your Can dump on vcan0

```
some example data is there in /mnt/zen-vault/ffa/nsingh/MobilEye_CANLogs/CAN_LOGs
```

```bash
canplayer -I <location_to_log_file> -l i vcan0=can0
```

Step 2 - Source the python env 
```bash
cd CAN_BUS_Tools 
source can_env/bin/activate
```
Step 3 - Run the Mobil Eye Visu Server
```bash
python3 CAN_BUS_Parser.py
# go to the server IP from terminal :8050
```


## Canplayer
The canplayer utility allows you to replay CAN messages from a log file. This is useful for testing and development without requiring actual CAN hardware.

### Basic Usage

To replay CAN messages from a log file:
```bash
# Navigate to your CAN logs directory
cd /home/nsingh/python_codes/CAN_Bus_Tools/CAN_LOGs

# Play a specific log file (replace with your desired file)
canplayer -I candump-2025-06-24_093934.log vcan0

# Play at real-time speed (default)
canplayer -I candump-2025-06-24_093934.log vcan0

# Play at 2x speed
canplayer -t 2 -I candump-2025-06-24_093934.log vcan0

# Play at 0.5x speed (slower)
canplayer -t 0.5 -I candump-2025-06-24_093934.log vcan0

# Play the log file in a continuous loop
canplayer -l i -I candump-2025-06-24_093934.log vcan0

# Play with loop and timing
canplayer -l i -t 2 -I candump-2025-06-24_093934.log vcan0


```

## Virtual CAN Setup
Follow the following guide to set up a virtual CAN on a host laptop to visualize/simulate a actual CAN port. 

### Required Modules

Install can-utils package
```bash
sudo apt update
sudo apt install can-utils
# Verify installation
which canplayer
which candump
which cansend
```
Check Kernel Support 
```bash
# Verify CAN support is loaded
lsmod | grep can
# If not loaded, load the modules
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan
```

### Create Virtual CAN Interface
```bash
# Create virtual CAN interface
sudo ip link add dev vcan0 type vcan
# Bring the interface up
sudo ip link set up vcan0
# Verify interface is created
ip link show vcan0
```

## PyEnv Setup

### Prerequisites
- Python 3.x installed on your system
- Access to terminal/command line

### Step 1: Navigate to Project Directory
```bash
cd /home/nsingh/python_codes
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv can_env
```

### Step 3: Activate Virtual Environment
```bash
source can_env/bin/activate
```

**Note:** You should see `(can_env)` in your terminal prompt when activated.

### Step 4: Install Required Dependencies
```bash
pip install python-can
pip install cantools
```

### Step 5: Verify Installation
```bash
python -c "import can; import cantools; print('Dependencies installed successfully!')"
```

### Step 6: Deactivate Environment (When Done)
```bash
deactivate
```

## Installation

[Installation instructions will go here]

## Usage

[Usage instructions will go here]