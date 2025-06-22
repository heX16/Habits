"""
Main Tracker Screen

Primary interface for habit tracking with 7-day table view.
Handles status cycling, date navigation, and habit display.
Uses KivyMD DataTable for better UI and functionality.
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
        
        # Data storage for table updates
        self.table_data = {}
        self.column_data = []
        self.row_data = []
        
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
            
            # Rebuild the data table
            self.rebuild_data_table(habits_data)
            
            # Update status
            habit_count = len(habits_data.get('habits', []))
            self.update_status_bar(f'Loaded {habit_count} habits')
            
        except Exception as e:
            Logger.error(f'MainTrackerScreen: Error loading habits data: {e}')
            self.update_status_bar(f'Error: {e}')
        finally:
            self.is_loading = False
        
    def rebuild_data_table(self, habits_data: dict):
        """Rebuild the data table with new data"""
        Logger.info('MainTrackerScreen: Rebuilding data table')
        
        if not self.table_container:
            Logger.warning('MainTrackerScreen: table_container widget not found')
            return
            
        # Prepare table data
        self.prepare_table_data(habits_data)
        
        # Remove existing table
        if self.data_table:
            self.table_container.remove_widget(self.data_table)
            
        # Create new data table
        self.data_table = MDDataTable(
            size_hint=(1, 1),
            use_pagination=False,
            check=False,
            column_data=self.column_data,
            row_data=self.row_data,
            elevation=2,
            background_color_header=[0.2, 0.2, 0.2, 1],
            background_color_cell=[0.1, 0.1, 0.1, 0.8],
            background_color_selected_cell=[0.3, 0.3, 0.8, 0.5],
        )
        
        # Bind table events
        self.data_table.bind(on_row_press=self.on_table_row_press)
        
        # Add table to container
        self.table_container.add_widget(self.data_table)
        
        Logger.info(f'MainTrackerScreen: Created table with {len(self.row_data)} rows')
        
    def prepare_table_data(self, habits_data: dict):
        """Prepare column and row data for the table"""
        if not self.current_start_date or not self.current_end_date:
            Logger.warning('MainTrackerScreen: Date range not set, cannot prepare table data')
            return
            
        # Get date headers
        date_headers = DateCalculator.get_date_headers(
            self.current_start_date, 
            self.current_end_date
        )
        
        # Prepare column data
        self.column_data = [
            ("Habit", dp(150))  # Habit name column
        ]
        
        # Add date columns
        for date_info in date_headers:
            day_name = date_info['day_short']
            date_short = date_info['date_short'] 
            column_name = f"{day_name}\n{date_short}"
            self.column_data.append((column_name, dp(60)))
            
        # Prepare row data
        self.row_data = []
        self.table_data = {}  # For mapping rows to habit data
        
        habits = habits_data.get('habits', [])
        today = date.today()
        
        for habit_idx, habit in enumerate(habits):
            habit_id = habit.get('id', 0)
            habit_name = habit.get('name', '')
            habit_levels = int(habit.get('levels', '0'))
            
            # Create row data starting with habit name
            row = [habit_name]
            
            # Add status for each date
            for date_info in date_headers:
                date_str = date_info['date']
                
                # Find status for this date
                status = 0
                for date_entry in habit.get('dates', []):
                    if date_entry['date'] == date_str:
                        status = date_entry.get('status', 0)
                        break
                        
                # Check if date is in the future
                is_future = DateCalculator.parse_date_string(date_str) > today
                
                # Convert status to display format
                status_display = self.get_status_display(status, habit_levels, is_future)
                row.append((status_display['icon'], status_display['color'], status_display['text']))
                
            self.row_data.append(tuple(row))
            
            # Store mapping for event handling
            self.table_data[habit_idx] = {
                'habit_id': habit_id,
                'habit_name': habit_name,
                'habit_levels': habit_levels,
                'dates': habit.get('dates', [])
            }
            
    def get_status_display(self, status: int, habit_levels: int, is_future: bool):
        """Convert status to display format for table cell"""
        if is_future:
            return {
                'icon': 'calendar-outline',
                'color': [0.5, 0.5, 0.5, 1],
                'text': ''
            }
            
        # Status icons and colors based on habit tracking system
        status_map = {
            0: {'icon': 'circle-outline', 'color': [0.6, 0.6, 0.6, 1], 'text': ''},
            1: {'icon': 'check-circle-outline', 'color': [0.3, 0.7, 0.3, 1], 'text': 'Mini'},
            2: {'icon': 'check-circle', 'color': [0.2, 0.8, 0.2, 1], 'text': 'Done'},
            3: {'icon': 'star-circle', 'color': [1.0, 0.8, 0.0, 1], 'text': 'Elite'},
            9: {'icon': 'close-circle', 'color': [0.8, 0.2, 0.2, 1], 'text': 'Fail'},
        }
        
        # Handle numeric statuses (10-19 map to 0-9)
        if 10 <= status <= 19:
            display_num = status - 10
            return {
                'icon': 'numeric-{}-circle'.format(display_num),
                'color': [0.2, 0.6, 0.8, 1],
                'text': str(display_num)
            }
            
        return status_map.get(status, status_map[0])
        
    def on_table_row_press(self, table_instance, row_instance):
        """Handle table row press - detect which cell was clicked"""
        Logger.info(f'MainTrackerScreen: Table row pressed')
        
        # Get row index
        try:
            row_index = self.row_data.index(row_instance.item)
            habit_data = self.table_data.get(row_index)
            
            if not habit_data:
                Logger.warning(f'MainTrackerScreen: No habit data found for row {row_index}')
                return
                
            Logger.info(f'MainTrackerScreen: Clicked on habit "{habit_data["habit_name"]}"')
            
            # For now, show a status menu for the first date (today)
            # TODO: Implement proper cell detection for specific date
            if self.current_start_date:
                today_str = date.today().strftime('%Y-%m-%d')
                current_status = self.get_habit_status_for_date(
                    habit_data['habit_id'], 
                    today_str
                )
                
                StatusMenuPopup.show_for_cell(
                    habit_data=habit_data,
                    current_status=current_status,
                    on_status_selected=lambda new_status: self.on_status_selected_from_menu(
                        habit_data['habit_id'], today_str, current_status, new_status
                    )
                )
                
        except (ValueError, AttributeError) as e:
            Logger.error(f'MainTrackerScreen: Error handling row press: {e}')
            
    def get_habit_status_for_date(self, habit_id: int, date_str: str) -> int:
        """Get current status for a habit on specific date"""
        for row_idx, habit_data in self.table_data.items():
            if habit_data['habit_id'] == habit_id:
                for date_entry in habit_data['dates']:
                    if date_entry['date'] == date_str:
                        return date_entry.get('status', 0)
                break
        return 0
        
    def on_status_selected_from_menu(self, habit_id: int, date_str: str, old_status: int, new_status: int):
        """Handle status selection from popup menu"""
        Logger.info(f'MainTrackerScreen: Status selected from menu - habit {habit_id}, date {date_str}, {old_status} → {new_status}')
        
        if new_status == old_status:
            self.update_status_bar('No status change')
            return
            
        # Update the database
        success = self.habits_model.update_habit_status(habit_id, date_str, new_status)
        
        if success:
            self.update_status_bar(f'Status updated to {new_status}')
            
            # Refresh the table
            if self.current_start_date and self.current_end_date:
                self.load_habits_data(self.current_start_date, self.current_end_date)
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