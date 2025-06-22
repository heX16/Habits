"""
Main Tracker Screen

Primary interface for habit tracking with 7-day table view.
Handles status cycling, date navigation, and habit display.
"""

from datetime import date, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty

from ..models import HabitsModel, DateCalculator
from ..widgets import StatusCell, HabitRow, DateHeader, StatusMenuPopup


class MainTrackerScreen(Screen):
    """Main screen for habit tracking table interface"""
    
    # Properties for data binding
    habits_model = ObjectProperty(None, allownone=True)
    current_date_offset = StringProperty('')
    week_label = StringProperty('This Week')
    is_loading = BooleanProperty(False)
    
    # UI widget references (connected from .kv file)
    habit_table = ObjectProperty(None, allownone=True)
    status_bar = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info('MainTrackerScreen: Initializing main tracker screen')
        
        # Initialize data model
        self.habits_model = HabitsModel()
        self.habits_model.bind(on_data_changed=self.on_data_changed)
        self.habits_model.bind(on_status_updated=self.on_status_updated)
        
        # Current date range
        self.current_start_date = None
        self.current_end_date = None
        
        # List of habit rows for management
        self.habit_rows = []
        
        # Schedule initial data load
        Clock.schedule_once(self.initialize_data, 0.1)
        
    def initialize_data(self, dt=None):
        """Initialize the screen with data"""
        Logger.info('MainTrackerScreen: Initializing data')
        self.load_current_week()
        
    def load_current_week(self):
        """Load data for the current week"""
        try:
            # Get current week range
            start_date, end_date = DateCalculator.get_date_range_from_offset(self.current_date_offset)
            self.load_habits_data(start_date, end_date)
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error loading current week: {e}')
            self.update_status_bar(f'Error loading data: {e}')
        
    def load_habits_data(self, start_date: date, end_date: date):
        """Load habits data for the specified date range"""
        Logger.info(f'MainTrackerScreen: Loading data from {start_date} to {end_date}')
        
        self.is_loading = True
        self.update_status_bar('Loading habits data...')
        
        try:
            # Load data from model
            habits_data = self.habits_model.load_habits_data(start_date, end_date)
            
            # Update current date range
            self.current_start_date = start_date
            self.current_end_date = end_date
            
            # Update week label
            self.week_label = DateCalculator.get_week_label(start_date, end_date)
            
            # Rebuild the UI table
            self.rebuild_habits_table(habits_data)
            
            # Update status
            habit_count = len(habits_data.get('habits', []))
            self.update_status_bar(f'Loaded {habit_count} habits')
            
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error loading habits data: {e}')
            self.update_status_bar(f'Error: {e}')
        finally:
            self.is_loading = False
        
    def rebuild_habits_table(self, habits_data: dict):
        """Rebuild the entire habits table"""
        Logger.info('MainTrackerScreen: Rebuilding habits table')
        
        if not self.habit_table:
            Logger.warning('MainTrackerScreen: habit_table widget not found')
            return
            
        # Clear existing table
        self.habit_table.clear_widgets()
        self.habit_rows.clear()
        
        # Get date headers
        if self.current_start_date is None or self.current_end_date is None:
            Logger.warning('MainTrackerScreen: Date range not set, cannot rebuild table')
            return
            
        date_headers = DateCalculator.get_date_headers(
            self.current_start_date, 
            self.current_end_date
        )
        
        # Set grid columns (1 for habit name + dates)
        self.habit_table.cols = 1 + len(date_headers)
        
        # Add header row
        self.add_header_row(date_headers)
        
        # Add habit rows
        habits = habits_data.get('habits', [])
        for habit in habits:
            self.add_habit_row(habit, date_headers)
            
        Logger.info(f'MainTrackerScreen: Added {len(habits)} habit rows')
        
    def add_header_row(self, date_headers: list):
        """Add the header row with date information"""
        # Empty cell for habit name column
        name_header = Label(
            text='Habit',
            size_hint=(None, None),
            size=(200, 60),
            font_size=14,
            bold=True,
            halign='center',
            valign='middle'
        )
        self.habit_table.add_widget(name_header)
        
        # Date headers
        for date_info in date_headers:
            header = DateHeader.create_from_date_info(date_info, width=50, height=60)
            self.habit_table.add_widget(header)
            
    def add_habit_row(self, habit_data: dict, date_headers: list):
        """Add a single habit row to the table"""
        # Process dates data for the row
        dates_data = []
        today = date.today()
        
        for date_info in date_headers:
            date_str = date_info['date']
            
            # Find status for this date
            status = 0
            for date_entry in habit_data.get('dates', []):
                if date_entry['date'] == date_str:
                    status = date_entry.get('status', 0)
                    break
                    
            # Check if date is in the future
            is_future = DateCalculator.parse_date_string(date_str) > today
            
            dates_data.append({
                'date': date_str,
                'status': status,
                'is_future': is_future
            })
            
        # Create habit row widget
        habit_row = HabitRow(
            habit_id=habit_data.get('id', 0),
            habit_name=habit_data.get('name', ''),
            habit_levels=int(habit_data.get('levels', '0')),
            dates_data=dates_data,
            is_readonly=self.habits_model.is_readonly,
            row_height=50,
            name_width=200,
            cell_size=50
        )
        
        # Bind events
        habit_row.bind(on_status_clicked=self.on_status_clicked)
        habit_row.bind(on_status_double_clicked=self.on_status_double_clicked)
        habit_row.bind(on_status_changed=self.on_status_changed)
        
        # Add to table and track
        self.habit_table.add_widget(habit_row)
        self.habit_rows.append(habit_row)
        
    def on_status_clicked(self, habit_row, habit_id: int, date_str: str, status: int):
        """Handle status cell single click"""
        Logger.info(f'MainTrackerScreen: Status clicked - habit {habit_id}, date {date_str}, status {status}')
        # The status cycling is already handled by StatusCell
        
    def on_status_double_clicked(self, habit_row, habit_id: int, date_str: str, status: int):
        """Handle status cell double click"""
        Logger.info(f'MainTrackerScreen: Status double-clicked - habit {habit_id}, date {date_str}')
        
        # Find habit data
        habit_data = self.habits_model.get_habit_data(habit_id)
        if not habit_data:
            Logger.warning(f'MainTrackerScreen: Habit data not found for ID {habit_id}')
            self.update_status_bar(f'Error: Habit {habit_id} not found')
            return
            
        # Show status selection menu
        StatusMenuPopup.show_for_cell(
            habit_data=habit_data,
            current_status=status,
            on_status_selected=lambda new_status: self.on_status_selected_from_menu(
                habit_id, date_str, status, new_status
            )
        )
        
        self.update_status_bar(f'Status menu for habit "{habit_data.get("name", "")}"')
        
    def on_status_changed(self, habit_row, habit_id: int, date_str: str, old_status: int, new_status: int):
        """Handle status change"""
        Logger.info(f'MainTrackerScreen: Status changed - habit {habit_id}, date {date_str}, {old_status} → {new_status}')
        
        # Update the database
        success = self.habits_model.update_habit_status(habit_id, date_str, new_status)
        
        if success:
            self.update_status_bar(f'Status updated for habit {habit_id}')
        else:
            self.update_status_bar('Failed to update status')
            # Revert the change in UI
            habit_row.update_cell_status(date_str, old_status)
    
    def on_status_selected_from_menu(self, habit_id: int, date_str: str, old_status: int, new_status: int):
        """Handle status selection from popup menu"""
        Logger.info(f'MainTrackerScreen: Status selected from menu - habit {habit_id}, date {date_str}, {old_status} → {new_status}')
        
        if new_status == old_status:
            # No change needed
            self.update_status_bar('No status change')
            return
            
        # Update the database
        success = self.habits_model.update_habit_status(habit_id, date_str, new_status)
        
        if success:
            # Update the UI
            for habit_row in self.habit_rows:
                if habit_row.habit_id == habit_id:
                    habit_row.update_cell_status(date_str, new_status)
                    break
                    
            self.update_status_bar(f'Status updated to {new_status}')
        else:
            self.update_status_bar('Failed to update status')
            
    def on_data_changed(self, habits_model):
        """Handle data model changes"""
        Logger.info('MainTrackerScreen: Data changed, refreshing view')
        if self.current_start_date and self.current_end_date:
            self.load_habits_data(self.current_start_date, self.current_end_date)
            
    def on_status_updated(self, habits_model, habit_id: int, date_str: str, status: int):
        """Handle individual status updates"""
        Logger.info(f'MainTrackerScreen: Status updated - habit {habit_id}, date {date_str} = {status}')
        # The UI should already be updated by the status change event
        
    def update_status_bar(self, message: str):
        """Update the status bar message"""
        if self.status_bar:
            self.status_bar.text = message
        Logger.info(f'MainTrackerScreen: Status - {message}')
        
    # Navigation methods
    def go_to_options(self):
        """Navigate to options screen"""
        Logger.info('MainTrackerScreen: Navigate to options')
        
        # Переключиться на экран настроек
        if self.manager:
            self.manager.current = 'options'
        else:
            Logger.warning('MainTrackerScreen: No screen manager found')
            self.update_status_bar('Navigation error: No screen manager')
        
    def navigate_previous(self):
        """Navigate to previous week"""
        Logger.info('MainTrackerScreen: Navigate to previous week')
        
        if self.current_start_date and self.current_end_date:
            prev_start, prev_end = DateCalculator.get_previous_week(
                self.current_start_date, self.current_end_date
            )
            self.load_habits_data(prev_start, prev_end)
        
    def navigate_next(self):
        """Navigate to next week"""
        Logger.info('MainTrackerScreen: Navigate to next week')
        
        if self.current_start_date and self.current_end_date:
            next_start, next_end = DateCalculator.get_next_week(
                self.current_start_date, self.current_end_date
            )
            self.load_habits_data(next_start, next_end)
        
    def go_to_today(self):
        """Navigate to current date"""
        Logger.info('MainTrackerScreen: Navigate to today')
        self.current_date_offset = ''
        self.load_current_week()
        
    def on_enter(self):
        """Called when screen is entered"""
        Logger.info('MainTrackerScreen: Screen entered')
        # Refresh data if needed
        if DateCalculator.is_midnight_refresh_needed():
            self.load_current_week()
        
    def on_leave(self):
        """Called when screen is left"""
        Logger.info('MainTrackerScreen: Screen left') 