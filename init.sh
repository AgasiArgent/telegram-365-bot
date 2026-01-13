#!/bin/bash
# Telegram 365 Bot - Development Environment Setup Script
# This script sets up and starts the development environment

set -e

echo "========================================"
echo "  Telegram 365 Bot - Development Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

# Check PostgreSQL
echo ""
echo "Checking PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "WARNING: PostgreSQL client (psql) not found"
    echo "Make sure PostgreSQL is installed and running"
fi

# Create virtual environment if it doesn't exist
echo ""
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "IMPORTANT: Edit .env file with your configuration:"
    echo "  - TELEGRAM_BOT_TOKEN: Get from @BotFather"
    echo "  - DATABASE_URL: Your PostgreSQL connection string"
    echo "  - ADMIN_PASSWORD: Secret password for admin access"
    echo "  - WEB_ADMIN_PASSWORD: Password for web panel login"
else
    echo ".env file exists"
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from src.database import init_db; init_db()"

# Print information
echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the bot:"
echo "  python3 src/main.py"
echo ""
echo "The web admin panel will be available at:"
echo "  http://localhost:5000"
echo ""
echo "Telegram Bot:"
echo "  Once started, users can interact via /start command"
echo "  Admins can use /admin <password> to unlock admin commands"
echo ""
echo "========================================"
