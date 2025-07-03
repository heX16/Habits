"""
Main Tracker Screen

Primary interface for habit tracking with 7-day table view.
Handles status cycling, date navigation, and habit display.
Uses custom table widget with logic similar to original script.js.
"""

from datetime import date, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from ..models import HabitsModel, DateCalculator
from ..widgets import StatusMenuPopup

# Import table widget utilities
from ..widgets import create_table_widget, recreate_table


class MainTrackerScreen(Screen):
    """Main screen for habit tracking table interface using custom table widget"""
    
    # Properties for data binding
    habits_model = ObjectProperty(None, allownone=True)
    current_date_offset = StringProperty('')
    week_label = StringProperty('This Week')
    is_loading = BooleanProperty(False)
    
    # UI widget references (connected from .kv file)
    table_container = ObjectProperty(None, allownone=True)
    status_bar = ObjectProperty(None, allownone=True)
    navigation_bar = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info('MainTrackerScreen: Initializing main tracker screen with custom table widget')
        
        # Initialize data model (will be set later by the main app)
        self.habits_model = None
        
        # Current date range
        self.current_start_date = None
        self.current_end_date = None
        
        # Table widget references
        self.table_scroll = None
        self.table_grid = None
        
        # Store habits data for reference (like habitsData in script.js)
        self.habits_data = {}
        
        # Schedule initial data load
        Clock.schedule_once(self.initialize_data, 0.1)
        
    def on_habits_model(self, instance, value):
        """Called when habits_model property changes"""
        if value is not None:
            Logger.info('MainTrackerScreen: Habits model connected')
            value.bind(on_data_changed=self.on_data_changed)
            value.bind(on_status_updated=self.on_status_updated)
            # Reload data if we have a date range
            if self.current_start_date and self.current_end_date:
                self.load_current_week()
        
    def initialize_data(self, dt=None):
        """Initialize the screen with data"""
        Logger.info('MainTrackerScreen: Initializing data')
        

        
        if self.habits_model:
            self.load_current_week()
        else:
            Logger.info('MainTrackerScreen: Waiting for habits model to be set')
        
    def load_current_week(self):
        """Load data for the current week"""
        try:
            # Get current week range
            start_date, end_date = DateCalculator.get_date_range_from_offset(self.current_date_offset)
            self.fetch_habits_data(start_date, end_date)
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error loading current week: {e}')
            self.update_status_bar(f'Error loading data: {e}')
        
    def fetch_habits_data(self, start_date: date, end_date: date):
        """
        Fetch habits data from the model (equivalent to fetchHabitsData in script.js)
        """
        Logger.info(f'MainTrackerScreen: Fetching data from {start_date} to {end_date}')
        
        if not self.habits_model:
            Logger.warning('MainTrackerScreen: No habits model available')
            self.update_status_bar('No data model available')
            return
        
        self.is_loading = True
        self.update_status_bar('Loading habits data...')
        
        try:
            # Load data from model
            habits_data = self.habits_model.load_habits_data(start_date, end_date)
            
            # Store the habits data globally (like habitsData in script.js)
            self.habits_data = habits_data
            Logger.info(f'MainTrackerScreen: After fetch, habits_data loaded: {len(habits_data.get("habits", []))} habits')
            
            # Update current date range
            self.current_start_date = start_date
            self.current_end_date = end_date
            
            # Update week label
            self.week_label = DateCalculator.get_week_label(start_date, end_date)
            
            # Render the table (equivalent to renderTable in script.js)
            self.render_table(habits_data, start_date, end_date)
            
            # Update status
            habit_count = len(habits_data.get('habits', []))
            self.update_status_bar(f'Loaded {habit_count} habits')
            
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error fetching habits data: {e}')
            self.update_status_bar(f'Error: {e}')
        finally:
            self.is_loading = False
        
    def render_table(self, data, start_date_str: date, end_date_str: date):
        """
        Render the table with habits data using create_table_widget (equivalent to renderTable in script.js)
        """
        Logger.info('MainTrackerScreen: Rendering table')
        
        if not self.table_container:
            Logger.warning('MainTrackerScreen: table_container widget not found')
            return
            
        # Get today for comparison (like in script.js)
        today = date.today()
        
        # Get dates from headers (equivalent to getting dates from dateHeaders in script.js)
        if not self.current_start_date or not self.current_end_date:
            Logger.warning('MainTrackerScreen: Date range not set, cannot render table')
            return
            
        date_headers = DateCalculator.get_date_headers(
            self.current_start_date, 
            self.current_end_date
        )
        dates = [date_info['date'] for date_info in date_headers]
        
        # Remove existing table
        if self.table_scroll:
            self.table_container.remove_widget(self.table_scroll)
            
        # Prepare table data as 2D array
        table_data = []
        
        # Create header row
        header_row = ['Habit']  # First column for habit name
        for date_info in date_headers:
            day_name = date_info['day_name']
            day_number = date_info['day_number']
            column_name = f"{day_name}\n{day_number}"
            header_row.append(column_name)
        table_data.append(header_row)
        
        # Fill data into rows (equivalent to data.habits.forEach in script.js)
        habits = data.get('habits', [])
        
        for habit_index, habit in enumerate(habits):
            row = self.initialize_habit_row(habit, dates, today)
            table_data.append(row)
            
        # Create new table using create_table_widget
        self.table_scroll, self.table_grid = create_table_widget(table_data)
        
        # Add table to container
        self.table_container.add_widget(self.table_scroll)
        
        # Fill table with data using recreate_table
        from ..widgets.table_widget import recreate_table
        recreate_table(self.table_grid, table_data)
        
        Logger.info(f'MainTrackerScreen: Rendered table with {len(habits)} habit rows')
        
    def initialize_habit_row(self, habit, dates, today):
        """
        Initialize a table row with habit data (equivalent to initializeHabitRow in script.js)
        
        :param habit: Habit data object
        :param dates: Array of dates in YYYY-MM-DD format  
        :param today: Current date
        :return: List representing table row data
        """
        # Set habit name in first cell (equivalent to setting habitLink in script.js)
        habit_name = habit.get('name', '')
        row = [habit_name]
        
        # Fill tracking data (equivalent to habit.tracking.forEach in script.js)
        habit_id = habit.get('id', 0)
        
        for date_index, date_str in enumerate(dates):
            # Find status for this date
            status = 0
            for date_entry in habit.get('dates', []):
                if date_entry['date'] == date_str:
                    status = date_entry.get('status', 0)
                    break
                    
            # Initialize habit cell (equivalent to initializeHabitCell in script.js)
            cell_data = self.initialize_habit_cell(status, habit_id, date_str, today, habit)
            row.append(cell_data)
            
        return row
        
    def initialize_habit_cell(self, status, habit_id, date_str, today, habit):
        """
        Initialize a single cell in the habit tracking table 
        (equivalent to initializeHabitCell in script.js)
        
        :param status: Status value for the cell
        :param habit_id: ID of the habit
        :param date_str: Date string in YYYY-MM-DD format
        :param today: Current date
        :param habit: Habit data object
        :return: String representation for the cell
        """
        # Parse cell date (equivalent to cellDate logic in script.js)
        cell_date = DateCalculator.parse_date_string(date_str)
        
        # Handle future dates (equivalent to isFutureDay logic in script.js)
        is_future_day = cell_date > today
        
        if is_future_day:
            # Future day styling
            return '...'
            
        # Get habit parameters (equivalent to getting habit data in script.js)
        is_bad_habit = habit.get('bad_habit', False)
        levels = int(habit.get('levels', 3))
        
        # Update display (equivalent to updateCellDisplay in script.js)
        return self.get_status_display_for_cell(status, habit_id, is_bad_habit, levels, is_future_day)
        
    def get_status_display_for_cell(self, status: int, habit_id: int, is_bad_habit: bool, levels: int, is_future_day: bool):
        """
        Get display format for a cell (equivalent to getStatusEmoji and updateCellDisplay logic in script.js)
        """
        if is_future_day:
            return '...'
            
        # Status display (equivalent to getStatusEmoji in script.js)
        if status == 0:
            # Empty status
            return '-'
        elif status == 1:
            # Mini done
            return 'Mini'
        elif status == 2:
            # Done
            return 'Done'
        elif status == 3:
            # Elite done
            return 'Elite'
        elif status == 9:
            # Failed
            return 'Fail'
        elif 10 <= status <= 19:
            # Numeric statuses (10-19 map to 0-9)
            display_num = status - 10
            return str(display_num)
        else:
            # Default
            return '-'
        
    def on_data_changed(self, habits_model):
        """Handle data model changes"""
        Logger.info('MainTrackerScreen: Data changed - ignoring to prevent loop')
        # Don't automatically refresh to prevent infinite loop
        # Manual refresh can be done via navigation or screen enter
            
    def on_status_updated(self, habits_model, habit_id: int, date_str: str, status: int):
        """Handle individual status updates"""
        Logger.info(f'MainTrackerScreen: Status updated - habit {habit_id}, date {date_str} = {status}')
        # The table should be refreshed by on_data_changed
        
    def update_status_bar(self, message: str):
        """Update the status bar message"""
        if self.status_bar:
            self.status_bar.text = message
        Logger.info(f'MainTrackerScreen: Status - {message}')
        
    # Navigation methods
    def go_to_options(self):
        """Navigate to options screen"""
        Logger.info('MainTrackerScreen: Navigate to options')
        
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
            self.fetch_habits_data(prev_start, prev_end)
        
    def navigate_next(self):
        """Navigate to next week"""
        Logger.info('MainTrackerScreen: Navigate to next week')
        
        if self.current_start_date and self.current_end_date:
            next_start, next_end = DateCalculator.get_next_week(
                self.current_start_date, self.current_end_date
            )
            self.fetch_habits_data(next_start, next_end)
        
    def go_to_today(self):
        """Navigate to current date (equivalent to goToToday in script.js)"""
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