"""
Habit Detail Screen

Screen for displaying individual habit calendar views with monthly statistics.
Equivalent to habit.html from the web version.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, NumericProperty

from datetime import date
from calendar import monthrange
from ..models import HabitsModel
from ..widgets.table_widget import create_calendar_table


# These classes are now replaced by InteractiveCalendarCell and create_calendar_table in table_widget.py


class HabitDetailScreen(Screen):
    """Screen for displaying individual habit calendar views"""
    
    # Properties
    habits_model = ObjectProperty(None, allownone=True)
    habit_id = NumericProperty(0)
    habit_name = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info('HabitDetailScreen: Initializing habit detail screen')
        
        # Initialize properties
        self.habits_model = None
        self.habit_id = 0
        self.habit_data = None
        
        # UI components
        self.content_layout = None
        self.calendars_container = None
        
        # Build UI
        Clock.schedule_once(self.build_ui, 0.1)
        
    def build_ui(self, dt=None):
        """Build the screen UI"""
        Logger.info('HabitDetailScreen: Building UI')
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header with habit name and back button
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Back button
        back_btn = Button(
            text='← Back',
            size_hint_x=None,
            width=dp(80),
            font_size='16sp',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        # Habit name
        self.habit_name_label = Label(
            text=self.habit_name or 'Habit Details',
            font_size='24sp',
            bold=True,
            halign='center'
        )
        self.habit_name_label.bind(size=self.habit_name_label.setter('text_size'))
        header_layout.add_widget(self.habit_name_label)
        
        # Empty space for balance
        header_layout.add_widget(Label(size_hint_x=None, width=dp(80)))
        
        main_layout.add_widget(header_layout)
        
        # Scrollable content area for calendars
        self.calendars_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(350)
        )
        self.calendars_container.bind(minimum_height=self.calendars_container.setter('height'))
        
        main_layout.add_widget(self.calendars_container)
        
        self.add_widget(main_layout)
        
    def load_habit_data(self, habit_id):
        """Load and display habit data"""
        Logger.info(f'HabitDetailScreen: Loading habit data for ID {habit_id}')
        
        self.habit_id = habit_id
        
        if not self.habits_model:
            Logger.warning('HabitDetailScreen: No habits model available')
            return
            
        try:
            # Load habit data for the last 2 months
            today = date.today()
            
            # Previous month
            if today.month == 1:
                prev_month = 12
                prev_year = today.year - 1
            else:
                prev_month = today.month - 1
                prev_year = today.year
                
            # Date range: first day of previous month to last day of current month
            start_date = date(prev_year, prev_month, 1)
            end_date = date(today.year, today.month, monthrange(today.year, today.month)[1])
            
            # Load data
            data = self.habits_model.load_habits_data(start_date, end_date)
            
            # Find our habit
            self.habit_data = None
            for habit in data.get('habits', []):
                if habit.get('id') == habit_id:
                    self.habit_data = habit
                    break
                    
            if not self.habit_data:
                Logger.error(f'HabitDetailScreen: Habit {habit_id} not found in data')
                return
                
            # Update UI
            self.habit_name = self.habit_data.get('name', 'Unknown Habit')
            if hasattr(self, 'habit_name_label'):
                self.habit_name_label.text = self.habit_name
                
            # Build calendars
            self._build_calendars(prev_year, prev_month, today.year, today.month)
            
        except Exception as e:
            Logger.error(f'HabitDetailScreen: Error loading habit data: {e}')
            
    def _build_calendars(self, prev_year, prev_month, curr_year, curr_month):
        """Build the calendar widgets using table_widget functions"""
        if not self.calendars_container or not self.habit_data:
            return
            
        # Clear existing calendars
        self.calendars_container.clear_widgets()
        
        # Create calendar data for previous month
        prev_month_data = self._create_calendar_data(prev_year, prev_month, 0)
        prev_scroll, prev_grid = create_calendar_table(
            prev_month_data, 
            self.habit_data, 
            self.habits_model
        )
        self.calendars_container.add_widget(prev_scroll)
        
        # Create calendar data for current month
        prev_month_days = monthrange(prev_year, prev_month)[1]
        curr_month_data = self._create_calendar_data(curr_year, curr_month, prev_month_days)
        curr_scroll, curr_grid = create_calendar_table(
            curr_month_data, 
            self.habit_data, 
            self.habits_model
        )
        self.calendars_container.add_widget(curr_scroll)
        
        Logger.info('HabitDetailScreen: Calendars built successfully')
    
    def _create_calendar_data(self, year, month, tracking_offset):
        """Create calendar data structure for create_calendar_table"""
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        # Calendar structure: [rows][cols]
        calendar_data = []
        
        # Month header row (spans all columns)
        header_row = [f'{month_names[month-1]} {year}'] + [''] * 7
        calendar_data.append(header_row)
        
        # Day headers row
        day_headers = ['Week', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        calendar_data.append(day_headers)
        
        # Get month details
        first_day, days_in_month = monthrange(year, month)
        first_day = (first_day + 1) % 7  # Convert to Sunday=0 format
        
        # Get tracking data
        tracking = self.habit_data.get('tracking', [])
        
        # Build calendar grid (6 weeks)
        day_num = 1
        for week in range(6):
            week_row = []
            
            # Week number
            if day_num <= days_in_month:
                week_date = date(year, month, day_num)
                week_num = week_date.isocalendar()[1]
                week_row.append(f'W{week_num}')
            else:
                week_row.append('')
            
            # Days of the week
            for day_col in range(7):
                if week == 0 and day_col < first_day:
                    # Empty cell before first day
                    week_row.append('')
                elif day_num > days_in_month:
                    # Empty cell after last day
                    week_row.append('')
                else:
                    # Valid day cell - create cell data dict
                    date_str = f'{year:04d}-{month:02d}-{day_num:02d}'
                    
                    # Get status from tracking data
                    status = 0
                    if tracking_offset + day_num - 1 < len(tracking):
                        status = tracking[tracking_offset + day_num - 1]
                    
                    cell_data = {
                        'day': day_num,
                        'status': status,
                        'date': date_str
                    }
                    week_row.append(cell_data)
                    day_num += 1
            
            calendar_data.append(week_row)
        
        return calendar_data
        
    def go_back(self, *args):
        """Go back to the previous screen"""
        Logger.info('HabitDetailScreen: Going back')
        
        if self.manager:
            self.manager.current = 'options'
        
    def on_enter(self):
        """Called when screen is entered"""
        Logger.info('HabitDetailScreen: Screen entered')
        
    def on_leave(self):
        """Called when screen is left"""
        Logger.info('HabitDetailScreen: Screen left') 