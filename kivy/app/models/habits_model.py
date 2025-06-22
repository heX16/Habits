"""
Habits Model

Main data model for the Kivy app that wraps the existing HabitsDatabase
and provides Kivy-specific data handling and business logic.
"""

import os
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Any
from kivy.logger import Logger
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, BooleanProperty

from common_lib.habits_database import HabitsDatabase, HabitStatus, HabitLevels


class HabitsModel(EventDispatcher):
    """
    Main data model for the Kivy app.
    Wraps HabitsDatabase and provides Kivy-specific functionality.
    """
    
    # Properties for data binding
    habits_data = ObjectProperty(None, allownone=True)
    is_loaded = BooleanProperty(False)
    is_readonly = BooleanProperty(False)
    
    def __init__(self, db_path: str = None, **kwargs):
        super().__init__(**kwargs)
        
        # Use default database path if not provided
        if db_path is None:
            db_path = os.path.join(os.path.expanduser('~'), 'habits.db')
            
        Logger.info(f'HabitsModel: Initializing with database: {db_path}')
        
        try:
            self.database = HabitsDatabase(
                db_path=db_path,
                create_tables_if_missing=True,
                create_db_file_if_missing=True
            )
            self.is_readonly = self.database.is_readonly()
            Logger.info('HabitsModel: Database initialized successfully')
            
        except Exception as e:
            Logger.error(f'HabitsModel: Failed to initialize database: {e}')
            raise
            
        # Current date range for the main view
        self.current_start_date = None
        self.current_end_date = None
        
        # Register events
        self.register_event_type('on_data_changed')
        self.register_event_type('on_status_updated')
        self.register_event_type('on_habits_reordered')
        
    def on_data_changed(self, *args):
        """Called when data is changed"""
        pass
        
    def on_status_updated(self, habit_id: int, date_str: str, status: int):
        """Called when a habit status is updated"""
        pass
        
    def on_habits_reordered(self, *args):
        """Called when habits are reordered"""
        pass
        
    def load_habits_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Load habits data for the specified date range.
        
        :param start_date: Start date for the range
        :param end_date: End date for the range
        :return: Dictionary with habits data
        """
        try:
            Logger.info(f'HabitsModel: Loading habits data from {start_date} to {end_date}')
            
            today = date.today()
            
            # Convert date objects to strings for database call
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            data = self.database.fetch_habits(start_date_str, end_date_str, today=today)
            
            # Transform the data format to match UI expectations
            self._transform_habits_data(data, start_date, end_date)
            
            # Store current date range
            self.current_start_date = start_date
            self.current_end_date = end_date
            
            # Add additional computed fields
            data['start_date'] = start_date
            data['end_date'] = end_date
            data['today'] = today
            data['is_readonly'] = self.is_readonly
            
            self.habits_data = data
            self.is_loaded = True
            
            Logger.info(f'HabitsModel: Loaded {len(data.get("habits", []))} habits')
            self.dispatch('on_data_changed')
            
            return data
            
        except Exception as e:
            Logger.error(f'HabitsModel: Error loading habits data: {e}')
            raise
            
    def _transform_habits_data(self, data: Dict[str, Any], start_date: date, end_date: date):
        """
        Transform the database format to UI format.
        Convert tracking array to dates array with date and status objects.
        
        :param data: Database data dictionary
        :param start_date: Start date for the range
        :param end_date: End date for the range
        """
        # Generate date list for the range
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
            
        # Transform each habit's tracking data
        for habit in data.get('habits', []):
            tracking = habit.get('tracking', [])
            dates = []
            
            # Convert tracking array to dates array
            for i, date_str in enumerate(date_list):
                status = tracking[i] if i < len(tracking) else 0
                dates.append({
                    'date': date_str,
                    'status': status
                })
                
            # Replace tracking with dates
            habit['dates'] = dates
            # Keep tracking for backward compatibility if needed
            # habit['tracking'] = tracking
            
    def update_habit_status(self, habit_id: int, date_str: str, status: int) -> bool:
        """
        Update the status of a habit for a specific date.
        
        :param habit_id: ID of the habit
        :param date_str: Date string in YYYY-MM-DD format
        :param status: New status value
        :return: True if successful, False otherwise
        """
        try:
            if self.is_readonly:
                Logger.warning('HabitsModel: Cannot update status - database is read-only')
                return False
                
            Logger.info(f'HabitsModel: Updating habit {habit_id} on {date_str} to status {status}')
            
            self.database.update_habit(habit_id, date_str, status)
            
            # Update local data if it's loaded
            if self.habits_data and 'habits' in self.habits_data:
                for habit in self.habits_data['habits']:
                    if habit['id'] == habit_id:
                        if 'dates' in habit:
                            for date_info in habit['dates']:
                                if date_info['date'] == date_str:
                                    date_info['status'] = status
                                    break
                        break
            
            self.dispatch('on_status_updated', habit_id, date_str, status)
            return True
            
        except Exception as e:
            Logger.error(f'HabitsModel: Error updating habit status: {e}')
            return False
            
    def get_habits_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all habits.
        
        :return: List of habit dictionaries
        """
        try:
            return self.database.get_habits_list()
        except Exception as e:
            Logger.error(f'HabitsModel: Error getting habits list: {e}')
            return []
            
    def add_habit(self, name: str) -> Optional[int]:
        """
        Add a new habit.
        
        :param name: Name of the habit
        :return: ID of the new habit or None if failed
        """
        try:
            if self.is_readonly:
                Logger.warning('HabitsModel: Cannot add habit - database is read-only')
                return None
                
            Logger.info(f'HabitsModel: Adding new habit: {name}')
            habit_id = self.database.add_habit(name)
            
            self.dispatch('on_data_changed')
            return habit_id
            
        except Exception as e:
            Logger.error(f'HabitsModel: Error adding habit: {e}')
            return None
            
    def delete_habit(self, habit_id: int) -> bool:
        """
        Delete a habit and all its tracking data.
        
        :param habit_id: ID of the habit to delete
        :return: True if successful, False otherwise
        """
        try:
            if self.is_readonly:
                Logger.warning('HabitsModel: Cannot delete habit - database is read-only')
                return False
                
            Logger.info(f'HabitsModel: Deleting habit {habit_id}')
            self.database.delete_habit(habit_id)
            
            self.dispatch('on_data_changed')
            return True
            
        except Exception as e:
            Logger.error(f'HabitsModel: Error deleting habit: {e}')
            return False
            
    def rename_habit(self, habit_id: int, new_name: str) -> bool:
        """
        Rename a habit.
        
        :param habit_id: ID of the habit
        :param new_name: New name for the habit
        :return: True if successful, False otherwise
        """
        try:
            if self.is_readonly:
                Logger.warning('HabitsModel: Cannot rename habit - database is read-only')
                return False
                
            Logger.info(f'HabitsModel: Renaming habit {habit_id} to: {new_name}')
            self.database.rename_habit(habit_id, new_name)
            
            self.dispatch('on_data_changed')
            return True
            
        except Exception as e:
            Logger.error(f'HabitsModel: Error renaming habit: {e}')
            return False
            
    def reorder_habit(self, habit_id: int, direction: str) -> bool:
        """
        Reorder a habit up or down.
        
        :param habit_id: ID of the habit
        :param direction: 'up' or 'down'
        :return: True if successful, False otherwise
        """
        try:
            if self.is_readonly:
                Logger.warning('HabitsModel: Cannot reorder habit - database is read-only')
                return False
                
            Logger.info(f'HabitsModel: Reordering habit {habit_id} {direction}')
            self.database.reorder_habit(habit_id, direction)
            
            self.dispatch('on_habits_reordered')
            self.dispatch('on_data_changed')
            return True
            
        except Exception as e:
            Logger.error(f'HabitsModel: Error reordering habit: {e}')
            return False
            
    def get_status_cycle(self, current_status: int, habit_levels: int = 0) -> int:
        """
        Get the next status in the cycle for clicking.
        
        :param current_status: Current status value
        :param habit_levels: Habit levels setting (0=all, 1=limited, 3=basic)
        :return: Next status value
        """
        # Standard cycle: 0 → 1 → 2 → 3 → 9 → 0
        if habit_levels == 1:  # Level 1: only basic statuses
            cycle = [HabitStatus.NOT_SET, HabitStatus.DONE, HabitStatus.FAIL]
        else:  # Level 3 or 0: full cycle
            cycle = [
                HabitStatus.NOT_SET,
                HabitStatus.DONE_MINI,
                HabitStatus.DONE,
                HabitStatus.DONE_ELITE,
                HabitStatus.FAIL
            ]
            
        try:
            current_index = cycle.index(current_status)
            next_index = (current_index + 1) % len(cycle)
            return cycle[next_index]
        except ValueError:
            # If current status is not in cycle, return first status
            return cycle[0]
            
    def get_status_icon_path(self, status: int) -> str:
        """
        Get the icon path for a status.
        
        :param status: Status value
        :return: Path to the icon file
        """
        icon_map = {
            HabitStatus.NOT_SET: None,
            HabitStatus.DONE_MINI: 'app/assets/images/done_mini.png',
            HabitStatus.DONE: 'app/assets/images/done.png',
            HabitStatus.DONE_ELITE: 'app/assets/images/done_elite.png',
            HabitStatus.FAIL: 'app/assets/images/fail.png',
        }
        
        # Handle numeric statuses (10-19)
        if 10 <= status <= 19:
            return None  # Will show number instead
            
        return icon_map.get(status)
        
    def get_status_text(self, status: int) -> str:
        """
        Get the text representation of a status.
        
        :param status: Status value
        :return: Text representation
        """
        if status == HabitStatus.NOT_SET:
            return ''
        elif 10 <= status <= 19:
            return str(status - 10)  # Show 0-9
        else:
            return ''  # Icons will be used
            
    def is_future_date(self, date_str: str) -> bool:
        """
        Check if a date is in the future.
        
        :param date_str: Date string in YYYY-MM-DD format
        :return: True if date is in the future
        """
        try:
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            return check_date > date.today()
        except ValueError:
            return False
            
    def get_habit_data(self, habit_id: int) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific habit by ID.
        
        :param habit_id: ID of the habit
        :return: Habit data dictionary or None if not found
        """
        try:
            # First try to get from loaded data
            if self.habits_data and 'habits' in self.habits_data:
                for habit in self.habits_data['habits']:
                    if habit.get('id') == habit_id:
                        return habit
            
            # If not found in loaded data, query database
            habits_list = self.database.get_habits_list()
            for habit in habits_list:
                if habit.get('id') == habit_id:
                    # Get habit parameters
                    habit['levels'] = self.database.get_param(habit_id, 'levels', '0')
                    habit['fail_by_default'] = self.database.get_param(habit_id, 'fail_by_default', '0')
                    habit['bad_habit'] = self.database.get_param(habit_id, 'bad_habit', '0')
                    return habit
                    
            Logger.warning(f'HabitsModel: Habit {habit_id} not found')
            return None
            
        except Exception as e:
            Logger.error(f'HabitsModel: Error getting habit data for ID {habit_id}: {e}')
            return None 