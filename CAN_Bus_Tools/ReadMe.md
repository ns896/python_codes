# CAN Bus Tools

This repository contains tools for replaying CAN data from recorded log files.

## Table of Contents
- Python Virtual Environment
  - [PyEnv Setup](#pyenv-setup)
  - [Installation](#installation)
  - [Usage](#usage)

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