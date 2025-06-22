#!/usr/bin/env python3
"""
Habits Simple Tracker - Kivy Mobile/Desktop Application

Main entry point for the Habits tracking application.
Migrated from Flask web version to cross-platform Kivy app.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Kivy imports
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config
from kivy.logger import Logger

# App imports
from app.screens.main_tracker_screen import MainTrackerScreen
from app.services.app_state_manager import AppStateManager


class HabitsApp(App):
    """Main Kivy application class for Habits Simple Tracker"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Habits Simple Tracker"
        self.app_state = None
        
    def build_config(self, config):
        """Build configuration for the app"""
        config.setdefaults('graphics', {
            'width': '800',
            'height': '600',
            'minimum_width': '600',
            'minimum_height': '400'
        })
        
    def build(self):
        """Build the main app interface"""
        # Initialize app state manager
        self.app_state = AppStateManager()
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add main tracker screen
        main_screen = MainTrackerScreen(name='main')
        sm.add_widget(main_screen)
        
        # Set current screen
        sm.current = 'main'
        
        Logger.info('HabitsApp: Application initialized successfully')
        return sm
        
    def on_start(self):
        """Called when the app starts"""
        Logger.info('HabitsApp: Application started')
        
    def on_stop(self):
        """Called when the app stops"""
        Logger.info('HabitsApp: Application stopped')
        if self.app_state:
            self.app_state.cleanup()


def main():
    """Main entry point"""
    # Configure Kivy settings
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.set('kivy', 'exit_on_escape', '1')
    
    # Create and run app
    app = HabitsApp()
    app.run()


if __name__ == '__main__':
    main() 