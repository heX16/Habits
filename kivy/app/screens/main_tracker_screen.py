"""
Main Tracker Screen

Primary interface for habit tracking with 7-day table view.
Handles status cycling, date navigation, and habit display.
Uses universal table widget with interactive cells.
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
from ..widgets.notification_manager import get_notification_manager

# Import universal table widget
from ..widgets import create_universal_table


class MainTrackerScreen(Screen):
    """Main screen for habit tracking table interface using universal table widget"""
    
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
        Logger.info('MainTrackerScreen: Initializing main tracker screen with universal table widget')
        
        # Initialize notifications (same as web version)
        self.notifications = get_notification_manager()
        
        # Initialize data model (will be set later by the main app)
        self.habits_model = None
        
        # Current date range
        self.current_start_date = None
        self.current_end_date = None
        
        # Table widget references
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
            self.notifications.show(f'Error loading data: {e}')
        
    def fetch_habits_data(self, start_date: date, end_date: date):
        """
        Fetch habits data from the model (equivalent to fetchHabitsData in script.js)
        """
        Logger.info(f'MainTrackerScreen: Fetching data from {start_date} to {end_date}')
        
        if not self.habits_model:
            Logger.warning('MainTrackerScreen: No habits model available')
            self.notifications.show('No data model available')
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
            self.notifications.show(f'Error loading habits: {e}')
        finally:
            self.is_loading = False
        
    def render_table(self, data, start_date_str: date, end_date_str: date):
        """
        Render the table with habits data using universal table widget
        """
        Logger.info('MainTrackerScreen: Rendering table with interactive cells')
        
        if not self.table_container:
            Logger.warning('MainTrackerScreen: table_container widget not found')
            return
            
        # Get today for comparison
        today = date.today()
        
        # Get dates from headers
        if not self.current_start_date or not self.current_end_date:
            Logger.warning('MainTrackerScreen: Date range not set, cannot render table')
            return
            
        date_headers = DateCalculator.get_date_headers(
            self.current_start_date, 
            self.current_end_date
        )
        dates = [date_info['date'] for date_info in date_headers]
        
        # Remove existing table
        if self.table_grid:
            self.table_container.remove_widget(self.table_grid)
            
        # Prepare table data as 2D array with cell configurations
        table_data = []
        
        # Create header row (simple labels)
        header_row = ['Habit']  # First column for habit name
        for date_info in date_headers:
            day_name = date_info['day_name']
            day_number = date_info['day_number']
            column_name = f"{day_name}\n{day_number}"
            header_row.append(column_name)
        table_data.append(header_row)
        
        # Fill data into rows with interactive cells
        habits = data.get('habits', [])
        
        for habit_index, habit in enumerate(habits):
            row = self.create_habit_row(habit, dates, today)
            table_data.append(row)
            
        # Create new table without ScrollView (table_container is now ScrollView)
        self.table_grid, _ = create_universal_table(table_data, with_scroll=False)
        
        # Add table grid directly to ScrollView container
        self.table_container.add_widget(self.table_grid)
        
        Logger.info(f'MainTrackerScreen: Rendered table with {len(habits)} habit rows')
        
    def create_habit_row(self, habit, dates, today):
        """
        Create a table row with habit data using interactive cells
        """
        row = []
        
        # First column: habit name (label)
        row.append(habit.get('name', ''))
        
        # Create a lookup dictionary for quick status access
        status_dict = {}
        for date_info in habit.get('dates', []):
            status_dict[date_info['date']] = date_info['status']
        
        # Rest of columns: status cells (interactive)
        for date_str in dates:
            status = status_dict.get(date_str, 0)
            
            # Check if this date is in the future
            is_future = False
            try:
                cell_date = date.fromisoformat(date_str)
                is_future = cell_date > today
            except ValueError:
                pass
                
            # Create interactive cell configuration
            cell_config = {
                'cell_mode': 'interactive',
                'value': status,
                'habit_id': habit.get('id', 0),
                'date_str': date_str,
                'habit_levels': int(habit.get('levels', 0)),
                'bad_habit': habit.get('bad_habit') == '1',
                'habits_model': self.habits_model
            }
            
            row.append(cell_config)
            
        return row
        
    def on_data_changed(self, habits_model):
        """Handle data changes in the model"""
        Logger.info('MainTrackerScreen: Data changed, reloading table')
        if self.current_start_date and self.current_end_date:
            self.load_current_week()
        
    def on_status_updated(self, habits_model, habit_id: int, date_str: str, status: int):
        """Handle individual status updates"""
        Logger.info(f'MainTrackerScreen: Status updated for habit {habit_id} on {date_str}: {status}')
        # Table will update automatically since cells are bound to the model
        
    def update_status_bar(self, message: str):
        """Update the status bar with a message"""
        if self.status_bar:
            self.status_bar.text = message
        Logger.info(f'MainTrackerScreen: Status: {message}')
        
    def go_to_options(self):
        """Navigate to options screen"""
        Logger.info('MainTrackerScreen: Navigating to options screen')
        self.manager.current = 'options'
        
    def navigate_previous(self):
        """Navigate to previous week"""
        Logger.info('MainTrackerScreen: Navigating to previous week')
        try:
            current_start, current_end = DateCalculator.get_date_range_from_offset(self.current_date_offset)
            previous_date = current_start - timedelta(days=7)
            self.current_date_offset = previous_date.strftime('%Y-%m-%d')
            self.load_current_week()
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error navigating to previous week: {e}')
            
    def navigate_next(self):
        """Navigate to next week"""
        Logger.info('MainTrackerScreen: Navigating to next week')
        try:
            current_start, current_end = DateCalculator.get_date_range_from_offset(self.current_date_offset)
            next_date = current_start + timedelta(days=7)
            self.current_date_offset = next_date.strftime('%Y-%m-%d')
            self.load_current_week()
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error navigating to next week: {e}')
            
    def go_to_today(self):
        """Navigate to current week"""
        Logger.info('MainTrackerScreen: Navigating to current week')
        self.current_date_offset = ''
        self.load_current_week()
        
    def on_enter(self):
        """Called when screen becomes active"""
        Logger.info('MainTrackerScreen: Screen entered')
        
    def on_leave(self):
        """Called when screen becomes inactive"""
        Logger.info('MainTrackerScreen: Screen left') 