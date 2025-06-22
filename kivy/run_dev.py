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

# Load configuration from config.ini if exists
config_file = Path(__file__).parent / 'config.ini'
if config_file.exists():
    Config.read(str(config_file))

# Development-specific settings
Config.set('kivy', 'log_level', '2')  # Debug level
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