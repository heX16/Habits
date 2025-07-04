#!/usr/bin/env python3
"""
Habits Simple Tracker - Kivy Version

Main application entry point for the Kivy-based habits tracking app.
Cross-platform habits tracker with 7-day table view.
Updated to use custom table widget with ScrollView and GridLayout.
"""

import os
import sys
import kivy
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger
from kivy.resources import resource_add_path
from kivy.lang import Builder

# Standard Kivy imports
from kivy.app import App

# Add the project root to the path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.screens import MainTrackerScreen, OptionsScreen, HabitEditScreen, HabitDetailScreen
from app.services.app_state_manager import AppStateManager





class HabitsApp(App):
    """Main Kivy application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info('HabitsApp: Initializing Kivy application')
        
        # App state manager
        self.state_manager = None
        
        # Screen manager
        self.screen_manager = None
        
        # Main screen
        self.main_screen = None
        
        # Options screen
        self.options_screen = None
        
        # Habit edit screen
        self.habit_edit_screen = None
        
        # Habit detail screen
        self.habit_detail_screen = None
        
    def build(self):
        """Build the application UI"""
        Logger.info('HabitsApp: Building application')
        
        try:
            # Initialize app state manager
            self.state_manager = AppStateManager()
            
            # Load the main screen layout
            kv_file = os.path.join(os.path.dirname(__file__), 'app', 'assets', 'kv', 'main_tracker.kv')
            if os.path.exists(kv_file):
                Builder.load_file(kv_file)
                Logger.info(f'HabitsApp: Loaded KV file: {kv_file}')
            else:
                Logger.warning(f'HabitsApp: KV file not found: {kv_file}')
            
            # Create screen manager
            self.screen_manager = ScreenManager()
            
            # Create main screen
            self.main_screen = MainTrackerScreen(name='main_tracker')
            
            # Create options screen
            self.options_screen = OptionsScreen(name='options')
            
            # Create habit edit screen
            self.habit_edit_screen = HabitEditScreen(name='habit_edit')
            
            # Create habit detail screen
            self.habit_detail_screen = HabitDetailScreen(name='habit_detail')
            
            # Connect screens to shared habits model
            if self.state_manager.is_database_ready():
                shared_model = self.state_manager.get_habits_model()
                self.main_screen.habits_model = shared_model
                self.options_screen.habits_model = shared_model
                self.habit_edit_screen.habits_model = shared_model
                self.habit_detail_screen.habits_model = shared_model
                Logger.info('HabitsApp: Connected screens to shared habits model')
            
            # Add screens to screen manager
            self.screen_manager.add_widget(self.main_screen)
            self.screen_manager.add_widget(self.options_screen)
            self.screen_manager.add_widget(self.habit_edit_screen)
            self.screen_manager.add_widget(self.habit_detail_screen)
            
            # Set initial screen
            self.screen_manager.current = 'main_tracker'
            
            # Set window title
            self.title = 'Habits Simple Tracker'
            
            Logger.info('HabitsApp: Application built successfully')
            return self.screen_manager
            
        except Exception as e:
            Logger.error(f'HabitsApp: Error building application: {e}')
            raise
            
    def on_start(self):
        """Called when the app starts"""
        Logger.info('HabitsApp: Application started')
        
        # Print database info
        if self.state_manager:
            db_info = self.state_manager.get_database_info()
            Logger.info(f'HabitsApp: Database info: {db_info}')
            
            # Add sample data if database is empty
            if db_info.get('habits_count', 0) == 0:
                Logger.info('HabitsApp: Database is empty, adding sample data')
                try:
                    self.state_manager.add_sample_data()
                    
                    # Refresh the main screen
                    if self.main_screen:
                        self.main_screen.load_current_week()
                        
                except Exception as e:
                    Logger.error(f'HabitsApp: Error adding sample data: {e}')
        
    def on_pause(self):
        """Called when the app is paused (Android)"""
        Logger.info('HabitsApp: Application paused')
        if self.state_manager:
            self.state_manager.on_app_pause()
        return True  # Return True to pause
        
    def on_resume(self):
        """Called when the app is resumed (Android)"""
        Logger.info('HabitsApp: Application resumed')
        if self.state_manager:
            self.state_manager.on_app_resume()
            
    def on_stop(self):
        """Called when the app is stopped"""
        Logger.info('HabitsApp: Application stopping')
        if self.state_manager:
            self.state_manager.on_app_stop()
            
    def get_application_config(self):
        """Get path to the application config file"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        Logger.info(f'HabitsApp: Using config file: {config_path}')
        return config_path


def main():
    """Main entry point"""
    Logger.info('Starting Habits Simple Tracker (Kivy Version)')
    
    try:
        # Create and run the app
        app = HabitsApp()
        app.run()
        
    except Exception as e:
        Logger.error(f'Failed to start application: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
        

if __name__ == '__main__':
    main() 