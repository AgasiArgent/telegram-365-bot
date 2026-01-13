#!/bin/bash
# Setup script for web-only development
set -e

echo "Setting up web-only development environment..."

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
fi

# Activate and install
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-web.txt

echo "Setup complete! Run: source venv/bin/activate && python run_web.py"
