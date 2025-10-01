#!/usr/bin/env bash

# setup_environment.sh - Complete environment setup for python_codes project
# This script creates a virtual environment and installs all required packages

echo "🚀 Setting up python_codes project environment..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install required packages
echo "📚 Installing required packages..."

# Core packages
pip install pyserial
pip install minimalmodbus

# CAN Bus packages
pip install python-can
pip install cantools

# Data visualization packages
pip install plotly
pip install dash
pip install numpy

# Additional useful packages
pip install asyncio
pip install dataclasses

echo "✅ Environment setup complete!"
echo ""
echo "To use the environment:"
echo "1. Activate: source .venv/bin/activate"
echo "2. Or use: ./krv-run.sh python3 your_script.py"
echo ""
echo "Installed packages:"
pip list


