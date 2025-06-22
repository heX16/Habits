"""
Main Tracker Screen

Primary interface for habit tracking with 7-day table view.
Handles status cycling, date navigation, and habit display.
"""

from kivy.uix.screenmanager import Screen
from kivy.logger import Logger


class MainTrackerScreen(Screen):
    """Main screen for habit tracking table interface"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info('MainTrackerScreen: Initializing main tracker screen')
        
    def on_enter(self):
        """Called when screen is entered"""
        Logger.info('MainTrackerScreen: Screen entered')
        
    def on_leave(self):
        """Called when screen is left"""
        Logger.info('MainTrackerScreen: Screen left')
        
    # Navigation methods (stubs for now)
    def go_to_options(self):
        """Navigate to options screen"""
        Logger.info('MainTrackerScreen: Navigate to options')
        
    def navigate_previous(self):
        """Navigate to previous week"""
        Logger.info('MainTrackerScreen: Navigate to previous week')
        
    def navigate_next(self):
        """Navigate to next week"""
        Logger.info('MainTrackerScreen: Navigate to next week')
        
    def go_to_today(self):
        """Navigate to current date"""
        Logger.info('MainTrackerScreen: Navigate to today') 