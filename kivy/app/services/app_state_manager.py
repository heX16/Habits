"""
App State Manager

Manages application state, lifecycle events, and data persistence.
Handles app startup, shutdown, and background/foreground transitions.
"""

import os
from kivy.logger import Logger
from kivy.properties import ObjectProperty

from ..models import HabitsModel


class AppStateManager:
    """Manages application state and lifecycle"""
    
    def __init__(self, db_path: str = None):
        Logger.info('AppStateManager: Initializing app state manager')
        
        self.is_initialized = False
        self.habits_model = None
        self.db_path = db_path
        
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
            
            # TODO: Setup background tasks for midnight refresh
            # TODO: Load app preferences
            
            self.is_initialized = True
            Logger.info('AppStateManager: App state manager initialized successfully')
            
        except Exception as e:
            Logger.error(f'AppStateManager: Failed to initialize: {e}')
            raise
            
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
            
    def on_app_pause(self):
        """Handle app pause event (mobile)"""
        Logger.info('AppStateManager: App paused')
        # TODO: Save current state
        # TODO: Schedule background tasks
        
    def on_app_resume(self):
        """Handle app resume event (mobile)"""
        Logger.info('AppStateManager: App resumed')
        # TODO: Check for midnight refresh
        # TODO: Restore state
        
    def on_app_stop(self):
        """Handle app stop event"""
        Logger.info('AppStateManager: App stopping')
        self.cleanup()
        
    def cleanup(self):
        """Cleanup resources on app shutdown"""
        Logger.info('AppStateManager: Cleaning up resources')
        
        try:
            # Close database connections
            if self.habits_model and hasattr(self.habits_model, 'database'):
                # Database connections are automatically closed by sqlite3
                Logger.info('AppStateManager: Database cleanup completed')
                
            # TODO: Save app state
            # TODO: Cancel background tasks
            
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