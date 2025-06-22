"""
Main Tracker Screen

Primary interface for habit tracking with 7-day table view.
Handles status cycling, date navigation, and habit display.
Uses KivyMD DataTable with logic similar to original script.js.
"""

from datetime import date, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.metrics import dp

from kivymd.uix.datatables import MDDataTable
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton

from ..models import HabitsModel, DateCalculator
from ..widgets import StatusMenuPopup


class MainTrackerScreen(Screen):
    """Main screen for habit tracking table interface using MDDataTable"""
    
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
        Logger.info('MainTrackerScreen: Initializing main tracker screen with MDDataTable')
        
        # Initialize data model
        self.habits_model = HabitsModel()
        self.habits_model.bind(on_data_changed=self.on_data_changed)
        self.habits_model.bind(on_status_updated=self.on_status_updated)
        
        # Current date range
        self.current_start_date = None
        self.current_end_date = None
        
        # Table widget reference
        self.data_table = None
        
        # Store habits data for reference (like habitsData in script.js)
        self.habits_data = {}
        
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
            self.fetch_habits_data(start_date, end_date)
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error loading current week: {e}')
            self.update_status_bar(f'Error loading data: {e}')
        
    def fetch_habits_data(self, start_date: date, end_date: date):
        """
        Fetch habits data from the model (equivalent to fetchHabitsData in script.js)
        """
        Logger.info(f'MainTrackerScreen: Fetching data from {start_date} to {end_date}')
        
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
        Render the table with habits data (equivalent to renderTable in script.js)
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
        
        # Remove existing table (equivalent to adjusting rows in script.js)
        if self.data_table:
            self.table_container.remove_widget(self.data_table)
            
        # Prepare column data
        column_data = [("Habit", dp(150))]  # First column for habit name
        
        # Add date columns
        for date_info in date_headers:
            day_name = date_info['day_name']
            day_number = date_info['day_number']
            column_name = f"{day_name}\n{day_number}"
            column_data.append((column_name, dp(70)))
            
        # Fill data into rows (equivalent to data.habits.forEach in script.js)
        row_data = []
        habits = data.get('habits', [])
        
        for habit_index, habit in enumerate(habits):
            row = self.initialize_habit_row(habit, dates, today)
            row_data.append(tuple(row))
            
        # Create new data table
        self.data_table = MDDataTable(
            size_hint=(1, 1),
            use_pagination=False,
            check=False,
            column_data=column_data,
            row_data=row_data,
            elevation=2,
            background_color_header=[0.2, 0.2, 0.3, 1],
            background_color_cell=[0.1, 0.1, 0.1, 0.9],
            background_color_selected_cell=[0.3, 0.3, 0.8, 0.6],
        )
        
        # Bind table events
        self.data_table.bind(on_row_press=self.on_table_row_press)
        
        # Add table to container
        self.table_container.add_widget(self.data_table)
        
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
        :return: Tuple for MDDataTable cell (icon, color, text)
        """
        # Parse cell date (equivalent to cellDate logic in script.js)
        cell_date = DateCalculator.parse_date_string(date_str)
        
        # Handle future dates (equivalent to isFutureDay logic in script.js)
        is_future_day = cell_date > today
        
        if is_future_day:
            # Future day styling
            return ('calendar-outline', [0.5, 0.5, 0.5, 1], '')
            
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
            return ('calendar-outline', [0.5, 0.5, 0.5, 1], '')
            
        # Status icons and colors (equivalent to getStatusEmoji in script.js)
        if status == 0:
            # Empty status - show menu button equivalent
            return ('circle-outline', [0.6, 0.6, 0.6, 1], '...')
        elif status == 1:
            # Mini done
            icon = 'check-circle-outline'
            color = [0.3, 0.7, 0.3, 1] if not is_bad_habit else [0.8, 0.2, 0.2, 1]
            return (icon, color, 'Mini')
        elif status == 2:
            # Done
            icon = 'check-circle'
            color = [0.2, 0.8, 0.2, 1] if not is_bad_habit else [0.8, 0.2, 0.2, 1]
            return (icon, color, 'Done')
        elif status == 3:
            # Elite done
            icon = 'star-circle'
            color = [1.0, 0.8, 0.0, 1] if not is_bad_habit else [0.8, 0.2, 0.2, 1]
            return (icon, color, 'Elite')
        elif status == 9:
            # Failed
            icon = 'close-circle'
            color = [0.8, 0.2, 0.2, 1] if not is_bad_habit else [0.2, 0.8, 0.2, 1]
            return (icon, color, 'Fail')
        elif 10 <= status <= 19:
            # Numeric statuses (10-19 map to 0-9)
            display_num = status - 10
            icon = f'numeric-{display_num}-circle' if display_num < 10 else 'numeric-9-plus-circle'
            color = [0.2, 0.6, 0.8, 1]
            return (icon, color, str(display_num))
        else:
            # Default
            return ('circle-outline', [0.6, 0.6, 0.6, 1], '')
            
    def on_table_row_press(self, table_instance, row_instance):
        """
        Handle table row press - equivalent to cell click logic in script.js
        """
        Logger.info(f'MainTrackerScreen: Table row pressed')
        
        try:
            row_data = row_instance.item
            habit_name = row_data[0]
            
            Logger.info(f'MainTrackerScreen: Clicked on habit: {habit_name}')
            
            # Find the habit data (equivalent to finding habit in habitsData in script.js)
            habit = None
            for h in self.habits_data.get('habits', []):
                if h.get('name') == habit_name:
                    habit = h
                    break
                    
            if not habit:
                Logger.warning(f'MainTrackerScreen: No habit data found for "{habit_name}"')
                return
                
            # For now, show status menu for today (equivalent to showStatusMenu in script.js)
            # TODO: Implement proper cell detection for specific date
            today_str = date.today().strftime('%Y-%m-%d')
            current_status = self.get_habit_status_for_date(habit['id'], today_str)
            
            # Show status menu (equivalent to showStatusMenu in script.js)
            StatusMenuPopup.show_for_cell(
                habit_data=habit,
                current_status=current_status,
                on_status_selected=lambda new_status: self.on_status_selected_from_menu(
                    habit['id'], today_str, current_status, new_status
                )
            )
            
            self.update_status_bar(f'Status menu for habit "{habit_name}"')
                
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error handling row press: {e}')
            
    def get_habit_status_for_date(self, habit_id: int, date_str: str) -> int:
        """Get current status for a habit on specific date"""
        for habit in self.habits_data.get('habits', []):
            if habit.get('id') == habit_id:
                for date_entry in habit.get('dates', []):
                    if date_entry['date'] == date_str:
                        return date_entry.get('status', 0)
                break
        return 0
        
    def on_status_selected_from_menu(self, habit_id: int, date_str: str, old_status: int, new_status: int):
        """
        Handle status selection from popup menu (equivalent to status update logic in script.js)
        """
        Logger.info(f'MainTrackerScreen: Status selected from menu - habit {habit_id}, date {date_str}, {old_status} → {new_status}')
        
        if new_status == old_status:
            self.update_status_bar('No status change')
            return
            
        # Update the database (equivalent to sendUpdate in script.js)
        success = self.send_update(habit_id, date_str, new_status)
        
        if success:
            self.update_status_bar(f'Status updated to {new_status}')
            
            # Refresh the table (equivalent to re-rendering in script.js)
            if self.current_start_date and self.current_end_date:
                self.fetch_habits_data(self.current_start_date, self.current_end_date)
        else:
            self.update_status_bar('Failed to update status')
            
    def send_update(self, habit_id: int, date_str: str, status: int) -> bool:
        """
        Send update request to backend (equivalent to sendUpdate in script.js)
        """
        try:
            success = self.habits_model.update_habit_status(habit_id, date_str, status)
            if success:
                Logger.info(f'MainTrackerScreen: Update successful for habit {habit_id} on {date_str}')
            else:
                Logger.error(f'MainTrackerScreen: Failed to update habit {habit_id} on {date_str}')
            return success
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error updating habit status: {e}')
            return False
            
    def on_data_changed(self, habits_model):
        """Handle data model changes"""
        Logger.info('MainTrackerScreen: Data changed, refreshing view')
        if self.current_start_date and self.current_end_date:
            self.fetch_habits_data(self.current_start_date, self.current_end_date)
            
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