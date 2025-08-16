"""
App State Manager

Manages application state, lifecycle events, and data persistence.
Handles app startup, shutdown, and background/foreground transitions.
"""

import os
import json
from datetime import datetime, time
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import ObjectProperty

from ..models import HabitsModel


class AppStateManager:
    """Manages application state and lifecycle"""
    
    def __init__(self, db_path: str = None):
        Logger.info('AppStateManager: Initializing app state manager')
        
        self.is_initialized = False
        self.habits_model = None
        self.db_path = db_path
        self.app_state = {}
        self.preferences = {}
        self.midnight_check_event = None
        
        self._initialize()
        
    def _initialize(self):
        """Initialize app state management"""
        try:
            # Initialize database path
            if self.db_path is None:
                # Use default path in user's home directory
                self.db_path = os.path.join(os.path.expanduser('~'), 'habits_kivy.db')
                
            Logger.info(f'AppStateManager: Using database: {self.db_path}')
            
            # Initialize habits model
            self.habits_model = HabitsModel(db_path=self.db_path)
            
            Logger.info('AppStateManager: Habits model initialized')
            
            # Load app preferences
            self._load_app_preferences()
            
            # Setup midnight refresh check
            self._setup_midnight_check()
            
            self.is_initialized = True
            Logger.info('AppStateManager: App state manager initialized successfully')
            
        except Exception as e:
            Logger.error(f'AppStateManager: Failed to initialize: {e}')
            raise
            
    def _load_app_preferences(self):
        """Load application preferences"""
        try:
            preferences_path = os.path.join(os.path.dirname(self.db_path), 'preferences.json')
            if os.path.exists(preferences_path):
                with open(preferences_path, 'r', encoding='utf-8') as f:
                    self.preferences = json.load(f)
                Logger.info('AppStateManager: Preferences loaded')
            else:
                # Default preferences
                self.preferences = {
                    'theme': 'light',
                    'auto_refresh': True,
                    'notifications_enabled': True
                }
                Logger.info('AppStateManager: Using default preferences')
                
        except Exception as e:
            Logger.warning(f'AppStateManager: Error loading preferences: {e}')
            self.preferences = {}
            
    def _save_app_preferences(self):
        """Save application preferences"""
        try:
            preferences_path = os.path.join(os.path.dirname(self.db_path), 'preferences.json')
            with open(preferences_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2)
            Logger.info('AppStateManager: Preferences saved')
        except Exception as e:
            Logger.error(f'AppStateManager: Error saving preferences: {e}')
            
    def _setup_midnight_check(self):
        """Setup midnight refresh check"""
        if self.preferences.get('auto_refresh', True):
            # Check every hour for midnight transition
            self.midnight_check_event = Clock.schedule_interval(self._check_midnight, 3600)
            Logger.info('AppStateManager: Midnight check scheduled')
            
    def _check_midnight(self, dt):
        """Check if we've passed midnight and need to refresh"""
        current_time = datetime.now().time()
        # Check if it's between midnight and 1 AM
        if time(0, 0) <= current_time <= time(1, 0):
            Logger.info('AppStateManager: Midnight detected, triggering refresh')
            self._trigger_midnight_refresh()
            
    def _trigger_midnight_refresh(self):
        """Trigger midnight refresh for all screens"""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and hasattr(app, 'main_screen'):
                app.main_screen.load_current_week()
                Logger.info('AppStateManager: Midnight refresh completed')
        except Exception as e:
            Logger.error(f'AppStateManager: Error during midnight refresh: {e}')
            
    def get_habits_model(self) -> HabitsModel:
        """
        Get the habits model instance.
        
        :return: HabitsModel instance
        """
        if not self.is_initialized:
            raise RuntimeError("AppStateManager not initialized")
            
        return self.habits_model
        
    def is_database_ready(self) -> bool:
        """
        Check if database is ready for use.
        
        :return: True if database is ready
        """
        return (self.is_initialized and 
                self.habits_model is not None and 
                self.habits_model.database is not None)
                
    def get_database_info(self) -> dict:
        """
        Get information about the database.
        
        :return: Dictionary with database information
        """
        if not self.is_database_ready():
            return {'status': 'not_ready'}
            
        try:
            habits_count = len(self.habits_model.get_habits_list())
            is_readonly = self.habits_model.is_readonly
            
            return {
                'status': 'ready',
                'path': self.db_path,
                'habits_count': habits_count,
                'is_readonly': is_readonly,
                'db_version': self.habits_model.database.DB_VERSION
            }
        except Exception as e:
            Logger.error(f'AppStateManager: Error getting database info: {e}')
            return {'status': 'error', 'error': str(e)}
            
    def get_preference(self, key: str, default=None):
        """Get application preference"""
        return self.preferences.get(key, default)
        
    def set_preference(self, key: str, value):
        """Set application preference"""
        self.preferences[key] = value
        self._save_app_preferences()
        
    def on_app_pause(self):
        """Handle app pause event (mobile)"""
        Logger.info('AppStateManager: App paused')
        
        # Save current app state
        self.app_state = {
            'pause_time': datetime.now().isoformat(),
            'current_screen': None  # Will be set by app if needed
        }
        
        # Cancel background tasks to save battery
        if self.midnight_check_event:
            self.midnight_check_event.cancel()
            self.midnight_check_event = None
            
        Logger.info('AppStateManager: App state saved for pause')
        
    def on_app_resume(self):
        """Handle app resume event (mobile)"""
        Logger.info('AppStateManager: App resumed')
        
        # Check if we need to refresh due to date change
        if 'pause_time' in self.app_state:
            try:
                pause_time = datetime.fromisoformat(self.app_state['pause_time'])
                now = datetime.now()
                
                # If we've been paused for more than 4 hours or date changed
                if (now - pause_time).total_seconds() > 4 * 3600 or now.date() != pause_time.date():
                    Logger.info('AppStateManager: Long pause detected, triggering refresh')
                    self._trigger_midnight_refresh()
                    
            except Exception as e:
                Logger.warning(f'AppStateManager: Error checking pause time: {e}')
                
        # Restore background tasks
        self._setup_midnight_check()
        
        # Clear app state
        self.app_state = {}
        Logger.info('AppStateManager: App state restored from resume')
        
    def on_app_stop(self):
        """Handle app stop event"""
        Logger.info('AppStateManager: App stopping')
        self.cleanup()
        
    def cleanup(self):
        """Cleanup resources on app shutdown"""
        Logger.info('AppStateManager: Cleaning up resources')
        
        try:
            # Save current app state
            self._save_app_preferences()
            
            # Cancel background tasks
            if self.midnight_check_event:
                self.midnight_check_event.cancel()
                self.midnight_check_event = None
                
            # Close database connections
            if self.habits_model and hasattr(self.habits_model, 'database'):
                # Database connections are automatically closed by sqlite3
                Logger.info('AppStateManager: Database cleanup completed')
                
            self.is_initialized = False
            Logger.info('AppStateManager: Cleanup completed')
            
        except Exception as e:
            Logger.error(f'AppStateManager: Error during cleanup: {e}')
            
    def reset_database(self):
        """Reset the database (for testing/debugging)"""
        Logger.warning('AppStateManager: Resetting database')
        
        if self.habits_model:
            try:
                self.habits_model.database.clear_db()
                self.habits_model.database.create_tables()
                Logger.info('AppStateManager: Database reset completed')
            except Exception as e:
                Logger.error(f'AppStateManager: Error resetting database: {e}')
                raise
                
    def add_sample_data(self):
        """Add sample data for testing"""
        Logger.info('AppStateManager: Adding sample data')
        
        if not self.is_database_ready():
            Logger.error('AppStateManager: Database not ready for sample data')
            return
            
        try:
            # Add sample habits
            sample_habits = [
                'Morning Exercise',
                'Read Book', 
                'Drink Water',
                'Meditation',
                'Healthy Meal'
            ]
            
            for habit_name in sample_habits:
                habit_id = self.habits_model.add_habit(habit_name)
                Logger.info(f'AppStateManager: Added sample habit: {habit_name} (ID: {habit_id})')
                
            Logger.info('AppStateManager: Sample data added successfully')
            
        except Exception as e:
            Logger.error(f'AppStateManager: Error adding sample data: {e}')
            raise 