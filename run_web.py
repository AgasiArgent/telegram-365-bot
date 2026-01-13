#!/usr/bin/env python3
"""Run only the web admin panel for testing (without Telegram bot)."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Minimal imports - only what's needed for Flask
from dotenv import load_dotenv
load_dotenv()

# Configure minimal settings
os.environ.setdefault('DATABASE_URL', 'sqlite:///./app.db')

from src.web import create_app
from src.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()

    print("Starting web panel on http://127.0.0.1:5000")
    app = create_app()
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
    )
