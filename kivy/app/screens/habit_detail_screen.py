"""
Habit Detail Screen

Screen for displaying individual habit calendar views with monthly statistics.
Equivalent to habit.html from the web version.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior

from datetime import date, datetime, timedelta
from calendar import monthrange
from ..models import HabitsModel
from ..widgets import StatusMenuPopup


class CalendarCell(ButtonBehavior, BoxLayout):
    """Individual calendar cell with status display and interaction"""
    
    def __init__(self, day_num=0, status=0, date_str='', habit_id=0, habit_levels=0, bad_habit=False, **kwargs):
        super().__init__(**kwargs)
        
        self.day_num = day_num
        self.status = status
        self.date_str = date_str
        self.habit_id = habit_id
        self.habit_levels = habit_levels
        self.bad_habit = bad_habit
        self.habits_model = None
        
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.padding = dp(2)
        
        self._build_cell()
        
    def _build_cell(self):
        """Build the cell content"""
        self.clear_widgets()
        
        # Day number label
        if self.day_num > 0:
            day_label = Label(
                text=str(self.day_num),
                font_size='12sp',
                size_hint=(1, 0.6),
                color=(0, 0, 0, 1)
            )
            self.add_widget(day_label)
            
            # Status display
            status_widget = self._create_status_widget()
            if status_widget:
                self.add_widget(status_widget)
        
        # Set background color based on status
        self._update_background()
        
    def _create_status_widget(self):
        """Create widget for status display"""
        if self.status == 0:
            return None
            
        # For numeric statuses (10-19), show number
        if 10 <= self.status <= 19:
            return Label(
                text=str(self.status - 10),
                font_size='10sp',
                size_hint=(1, 0.4),
                color=(1, 1, 1, 1)
            )
        else:
            # For other statuses, try to show icon
            icon_path = self._get_status_icon_path()
            if icon_path:
                return Image(
                    source=icon_path,
                    size_hint=(1, 0.4)
                )
        
        return None
        
    def _get_status_icon_path(self):
        """Get icon path for status"""
        from common_lib.habits_database import HabitStatus
        
        icon_map = {
            HabitStatus.DONE_MINI: 'app/assets/images/done_mini.png',
            HabitStatus.DONE: 'app/assets/images/done.png',
            HabitStatus.DONE_ELITE: 'app/assets/images/done_elite.png',
            HabitStatus.FAIL: 'app/assets/images/fail.png',
        }
        
        from common_lib.habits_database import HabitStatus
        try:
            return icon_map.get(HabitStatus(self.status))
        except ValueError:
            return None
        
    def _update_background(self):
        """Update background color based on status"""
        from common_lib.habits_database import HabitStatus
        
        # Default background
        bg_color = (0.95, 0.95, 0.95, 1)  # Light gray
        
        if self.status == 0:
            bg_color = (1, 1, 1, 1)  # White
        elif self.status == HabitStatus.DONE_MINI:
            bg_color = (0.7, 1, 0.7, 1) if not self.bad_habit else (1, 1, 0.7, 1)
        elif self.status == HabitStatus.DONE:
            bg_color = (0.5, 1, 0.5, 1) if not self.bad_habit else (1, 0.7, 0.7, 1)
        elif self.status == HabitStatus.DONE_ELITE:
            bg_color = (1, 0.84, 0, 1) if not self.bad_habit else (1, 0.5, 0.5, 1)
        elif self.status == HabitStatus.FAIL:
            bg_color = (1, 0.7, 0.7, 1) if not self.bad_habit else (0.5, 1, 0.5, 1)
        elif 10 <= self.status <= 19:
            bg_color = (0.5, 1, 0.5, 1) if not self.bad_habit else (1, 0.7, 0.7, 1)
        
        # Check if date is in the future
        if self.date_str and self._is_future_date():
            bg_color = (0.9, 0.9, 0.9, 1)  # Gray for future dates
        
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*bg_color)
            Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_background_rect, size=self._update_background_rect)
        
    def _update_background_rect(self, *args):
        """Update background rectangle position/size"""
        if self.canvas.before.children:
            self.canvas.before.children[-1].pos = self.pos
            self.canvas.before.children[-1].size = self.size
            
    def _is_future_date(self):
        """Check if this cell's date is in the future"""
        if not self.date_str:
            return False
            
        try:
            cell_date = datetime.strptime(self.date_str, '%Y-%m-%d').date()
            return cell_date > date.today()
        except ValueError:
            return False
    
    def on_press(self):
        """Handle single click - cycle status"""
        if not self.habits_model or not self.date_str or self.day_num <= 0:
            return
            
        if self._is_future_date():
            return  # Don't allow changes to future dates
            
        # Get next status in cycle
        next_status = self.habits_model.get_status_cycle(self.status, self.habit_levels)
        
        # Update status
        success = self.habits_model.update_habit_status(self.habit_id, self.date_str, next_status)
        
        if success:
            self.status = next_status
            self._build_cell()
            
    def on_touch_down(self, touch):
        """Handle touch events"""
        if self.collide_point(*touch.pos):
            if hasattr(touch, 'is_double_tap') and touch.is_double_tap:
                self._show_status_menu()
                return True
            else:
                # Single tap - cycle status
                self.on_press()
                return True
        return super().on_touch_down(touch)
        
    def _show_status_menu(self):
        """Show status menu popup"""
        if not self.habits_model or not self.date_str or self.day_num <= 0:
            return
            
        if self._is_future_date():
            return  # Don't allow changes to future dates
            
        # Create habit data for popup
        habit_data = {
            'name': 'Habit',
            'levels': self.habit_levels,
            'bad_habit': '1' if self.bad_habit else '0',
            'mode': f'level{self.habit_levels}' if self.habit_levels in [1, 10] else 'level3'
        }
        
        # Show status menu popup
        popup = StatusMenuPopup(
            habit_data=habit_data,
            current_status=self.status,
            on_status_selected=self._on_status_changed
        )
        popup.open()
        
    def _on_status_changed(self, new_status):
        """Handle status change from popup"""
        if not self.habits_model or not self.date_str:
            return
            
        # Update status in model
        success = self.habits_model.update_habit_status(self.habit_id, self.date_str, new_status)
        
        if success:
            self.status = new_status
            self._build_cell()


class MonthCalendar(GridLayout):
    """Monthly calendar widget"""
    
    def __init__(self, year, month, habit_data, habits_model, tracking_offset=0, **kwargs):
        super().__init__(**kwargs)
        
        self.year = year
        self.month = month
        self.habit_data = habit_data
        self.habits_model = habits_model
        self.tracking_offset = tracking_offset
        
        self.cols = 8  # Date column + 7 days
        self.rows = 7  # Header + 6 weeks
        self.spacing = dp(2)
        self.size_hint_y = None
        self.height = dp(300)
        
        self._build_calendar()
        
    def _build_calendar(self):
        """Build the calendar grid"""
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        # Month header (spans all columns)
        month_label = Label(
            text=f'{month_names[self.month]} {self.year}',
            size_hint=(1, None),
            height=dp(40),
            font_size='18sp',
            bold=True
        )
        
        # Add empty cells for the month header row
        for i in range(self.cols):
            if i == 0:
                self.add_widget(month_label)
            else:
                self.add_widget(Label(text=''))
        
        # Day headers
        self.add_widget(Label(text='Week', font_size='12sp', bold=True))
        for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
            self.add_widget(Label(text=day, font_size='12sp', bold=True))
            
        # Calendar cells
        first_day, days_in_month = monthrange(self.year, self.month)
        first_day = (first_day + 1) % 7  # Convert to Sunday=0 format
        
        tracking = self.habit_data.get('tracking', [])
        habit_id = self.habit_data.get('id', 0)
        habit_levels = int(self.habit_data.get('levels', 0))
        bad_habit = self.habit_data.get('bad_habit') == '1'
        
        day_num = 1
        for week in range(6):  # 6 weeks maximum
            # Week label
            if day_num <= days_in_month:
                week_date = date(self.year, self.month, day_num)
                week_num = week_date.isocalendar()[1]
                week_label = Label(
                    text=f'W{week_num}',
                    font_size='10sp',
                    size_hint=(None, None),
                    size=(dp(30), dp(40))
                )
                self.add_widget(week_label)
            else:
                self.add_widget(Label(text=''))
            
            # Days of the week
            for day_col in range(7):
                if week == 0 and day_col < first_day:
                    # Empty cell before first day
                    self.add_widget(Label(text=''))
                elif day_num > days_in_month:
                    # Empty cell after last day
                    self.add_widget(Label(text=''))
                else:
                    # Valid day cell
                    date_str = f'{self.year:04d}-{self.month+1:02d}-{day_num:02d}'
                    
                    # Get status from tracking data
                    status = 0
                    if self.tracking_offset + day_num - 1 < len(tracking):
                        status = tracking[self.tracking_offset + day_num - 1]
                    
                    cell = CalendarCell(
                        day_num=day_num,
                        status=status,
                        date_str=date_str,
                        habit_id=habit_id,
                        habit_levels=habit_levels,
                        bad_habit=bad_habit
                    )
                    cell.habits_model = self.habits_model
                    self.add_widget(cell)
                    
                    day_num += 1


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
        
        # Scrollable content area
        scroll_view = ScrollView()
        self.calendars_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(350)
        )
        self.calendars_container.bind(minimum_height=self.calendars_container.setter('height'))
        
        scroll_view.add_widget(self.calendars_container)
        main_layout.add_widget(scroll_view)
        
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
        """Build the calendar widgets"""
        if not self.calendars_container or not self.habit_data:
            return
            
        # Clear existing calendars
        self.calendars_container.clear_widgets()
        
        # Previous month calendar
        prev_month_calendar = MonthCalendar(
            year=prev_year,
            month=prev_month - 1,  # Convert to 0-indexed
            habit_data=self.habit_data,
            habits_model=self.habits_model,
            tracking_offset=0
        )
        self.calendars_container.add_widget(prev_month_calendar)
        
        # Current month calendar
        prev_month_days = monthrange(prev_year, prev_month)[1]
        curr_month_calendar = MonthCalendar(
            year=curr_year,
            month=curr_month - 1,  # Convert to 0-indexed
            habit_data=self.habit_data,
            habits_model=self.habits_model,
            tracking_offset=prev_month_days
        )
        self.calendars_container.add_widget(curr_month_calendar)
        
        Logger.info('HabitDetailScreen: Calendars built successfully')
        
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