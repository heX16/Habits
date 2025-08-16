#!/usr/bin/env python3
"""
Development runner for Habits Simple Tracker Kivy App

This script provides enhanced development features:
- Hot reload configuration
- Debug logging
- Development-specific settings
"""

import os
import sys
from pathlib import Path

# Set development environment
os.environ['KIVY_DEV_MODE'] = '1'

# Configure Kivy before importing
from kivy.config import Config
from kivy.logger import Logger

# Application constants
from config_constants import CONFIG_FILENAME

# Load configuration from habits.ini if exists
config_file = Path(__file__).parent / CONFIG_FILENAME
if config_file.exists():
    Config.read(str(config_file))
    Logger.info(f'Development: Loaded config from {config_file}')
else:
    Logger.error(f'Development: Config file not found: {config_file}')
    Logger.warning('Development: Using default Kivy configuration')

# Development-specific settings
Config.set('kivy', 'log_level', 'debug')  # Debug level
Config.set('graphics', 'show_cursor', '1')
Config.set('graphics', 'resizable', '1')

# Import and run main app
from main import main

if __name__ == '__main__':
    print("🚀 Starting Habits Simple Tracker in development mode...")
    print("📁 Project directory:", Path(__file__).parent)
    print("🔧 Debug logging enabled")
    print("⌨️  Press Ctrl+C to stop\n")

    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Development session ended")
        sys.exit(0)
