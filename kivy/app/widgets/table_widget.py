"""
Universal Table Widget

Provides a single universal cell class and table creation function.
Replaces all previous cell types (Label, StatusCell, InteractiveCalendarCell)
with one flexible UniversalCell class.
"""

from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.event import EventDispatcher
from datetime import date, datetime
import os


class UniversalCell(ButtonBehavior, BoxLayout, EventDispatcher):
    """
    Universal cell widget that can work in multiple modes:
    - 'label': Simple text label (for headers)
    - 'interactive': Interactive status cell (for main table)
    - 'calendar': Calendar cell with day number (for calendar view)
    """
    
    # Core properties
    cell_mode = StringProperty('label')  # 'label', 'interactive', 'calendar'
    text = StringProperty('')
    
    # Status properties (for interactive/calendar modes)
    status = NumericProperty(0)
    habit_id = NumericProperty(0)
    date_str = StringProperty('')
    habit_levels = NumericProperty(0)  # 0=all, 1=limited, 3=basic, 10=numeric
    bad_habit = BooleanProperty(False)
    
    # Calendar properties (for calendar mode)
    day_num = NumericProperty(0)
    
    # Visual properties
    is_future = BooleanProperty(False)
    is_readonly = BooleanProperty(False)
    
    # Model reference
    habits_model = ObjectProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set up the layout
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.padding = dp(2)
        
        # Double-click detection
        self.last_click_time = 0
        self.double_click_timeout = 0.3
        self.single_click_scheduled = False
        
        # Content widgets
        self.main_label = None
        self.status_widget = None
        
        # Register events
        self.register_event_type('on_status_clicked')
        self.register_event_type('on_status_double_clicked')
        self.register_event_type('on_status_changed')
        
        # Bind properties
        self.bind(cell_mode=self._rebuild_cell)
        self.bind(text=self._update_content)
        self.bind(status=self._update_content)
        self.bind(day_num=self._update_content)
        self.bind(is_future=self._update_visual_state)
        self.bind(is_readonly=self._update_visual_state)
        
        # Build initial content
        Clock.schedule_once(lambda dt: self._rebuild_cell(), 0)
        
    def _rebuild_cell(self, *args):
        """Rebuild cell content based on mode"""
        self.clear_widgets()
        
        if self.cell_mode == 'label':
            self._build_label_cell()
        elif self.cell_mode == 'interactive':
            self._build_interactive_cell()
        elif self.cell_mode == 'calendar':
            self._build_calendar_cell()
        
        self._update_content()
        self._update_visual_state()
        
    def _build_label_cell(self):
        """Build simple label cell"""
        self.main_label = Label(
            text=self.text,
            size_hint=(1, 1),
            halign="center",
            valign="middle",
            color=(0, 0, 0, 1)
        )
        self.main_label.bind(size=self.main_label.setter('text_size'))
        self.add_widget(self.main_label)
        
    def _build_interactive_cell(self):
        """Build interactive status cell"""
        # Status icon/text widget
        self.status_widget = Label(
            text='',
            size_hint=(1, 1),
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.status_widget)
        
    def _build_calendar_cell(self):
        """Build calendar cell with day number and status"""
        if self.day_num > 0:
            # Day number label
            self.main_label = Label(
                text=str(self.day_num),
                font_size='12sp',
                size_hint=(1, 0.6),
                halign="center",
                valign="middle",
                color=(0, 0, 0, 1)
            )
            self.main_label.bind(size=self.main_label.setter('text_size'))
            self.add_widget(self.main_label)
            
            # Status widget
            self.status_widget = Label(
                text='',
                font_size='10sp',
                size_hint=(1, 0.4),
                halign="center",
                valign="middle",
                color=(1, 1, 1, 1)
            )
            self.add_widget(self.status_widget)
        
    def _update_content(self, *args):
        """Update cell content based on current state"""
        if self.cell_mode == 'label':
            if self.main_label:
                self.main_label.text = self.text
                
        elif self.cell_mode in ['interactive', 'calendar']:
            if self.status_widget:
                if self.status == 0:
                    self.status_widget.text = ''
                elif 10 <= self.status <= 19:
                    # Numeric status (0-9)
                    self.status_widget.text = str(self.status - 10)
                else:
                    # Try to show icon (fallback to emoji)
                    icon_path = self._get_status_icon_path()
                    if icon_path and os.path.exists(icon_path):
                        # Replace label with image
                        if isinstance(self.status_widget, Label):
                            self.remove_widget(self.status_widget)
                            self.status_widget = Image(
                                source=icon_path,
                                size_hint=(1, 0.4) if self.cell_mode == 'calendar' else (1, 1),
                                allow_stretch=True,
                                keep_ratio=True
                            )
                            self.add_widget(self.status_widget)
                    else:
                        # Fallback to emoji
                        emoji = self._get_status_emoji()
                        self.status_widget.text = emoji
                        
        self._update_background()
        
    def _get_status_icon_path(self):
        """Get icon path for status"""
        icon_map = {
            1: 'app/assets/images/done_mini.png',  # DONE_MINI
            2: 'app/assets/images/done.png',       # DONE
            3: 'app/assets/images/done_elite.png', # DONE_ELITE
            9: 'app/assets/images/fail.png',       # FAIL
        }
        return icon_map.get(self.status, '')
        
    def _get_status_emoji(self):
        """Get emoji for status (fallback)"""
        emoji_map = {
            1: '✓',  # DONE_MINI
            2: '✓✓', # DONE
            3: '★',  # DONE_ELITE
            9: '✗',  # FAIL
        }
        return emoji_map.get(self.status, '')
        
    def _update_background(self):
        """Update background color based on status"""
        if self.cell_mode == 'label':
            bg_color = (0.95, 0.95, 0.95, 1)  # Light gray for headers
        else:
            bg_color = self._get_status_color()
            
        # Apply future date dimming
        if self.is_future:
            bg_color = (0.9, 0.9, 0.9, 1)  # Gray for future dates
            
        with self.canvas.before:
            Color(*bg_color)
            Rectangle(pos=self.pos, size=self.size)
            
        self.bind(pos=self._update_background_rect, size=self._update_background_rect)
        
    def _get_status_color(self):
        """Get background color for status"""
        if self.status == 0:
            return (1, 1, 1, 1)  # White for not set
        elif self.status == 1:  # DONE_MINI
            color = (0.8, 1, 0.8, 1) if not self.bad_habit else (1, 0.8, 0.8, 1)
        elif self.status == 2:  # DONE
            color = (0.6, 1, 0.6, 1) if not self.bad_habit else (1, 0.6, 0.6, 1)
        elif self.status == 3:  # DONE_ELITE
            color = (0.4, 1, 0.4, 1) if not self.bad_habit else (1, 0.4, 0.4, 1)
        elif self.status == 9:  # FAIL
            color = (1, 0.6, 0.6, 1) if not self.bad_habit else (0.6, 1, 0.6, 1)
        elif 10 <= self.status <= 19:  # NUMERIC
            if self.status == 10:  # 0
                color = (0.8, 0.8, 1, 1)  # Blue for 0
            else:
                color = (1, 0.8, 0.8, 1) if not self.bad_habit else (0.8, 1, 0.8, 1)
        else:
            color = (1, 1, 1, 1)  # White for unknown
            
        return color
        
    def _update_background_rect(self, *args):
        """Update background rectangle position/size"""
        if self.canvas.before.children:
            self.canvas.before.children[-1].pos = self.pos
            self.canvas.before.children[-1].size = self.size
            
    def _update_visual_state(self, *args):
        """Update visual state based on readonly/future flags"""
        if self.is_future:
            self.opacity = 0.5
            self.disabled = True
        elif self.is_readonly:
            self.opacity = 0.8
            self.disabled = True
        else:
            self.opacity = 1.0
            self.disabled = False
            
    def _is_future_date(self):
        """Check if this cell's date is in the future"""
        if not self.date_str:
            return False
            
        try:
            cell_date = datetime.strptime(self.date_str, '%Y-%m-%d').date()
            return cell_date > date.today()
        except ValueError:
            return False
            
    # Event handlers
    def on_status_clicked(self, habit_id: int, date_str: str, current_status: int):
        """Event for single click"""
        pass
        
    def on_status_double_clicked(self, habit_id: int, date_str: str, current_status: int):
        """Event for double click"""
        pass
        
    def on_status_changed(self, habit_id: int, date_str: str, old_status: int, new_status: int):
        """Event for status change"""
        pass
        
    def on_press(self):
        """Handle button press"""
        if self.cell_mode == 'label':
            return  # Labels are not interactive
            
        current_time = Clock.get_time()
        
        # Check if it's a double-click
        if current_time - self.last_click_time < self.double_click_timeout:
            self._handle_double_click()
            # Cancel scheduled single click
            if self.single_click_scheduled:
                Clock.unschedule(self._handle_single_click)
                self.single_click_scheduled = False
        else:
            # Schedule single click handling
            Clock.schedule_once(lambda dt: self._handle_single_click(), self.double_click_timeout)
            self.single_click_scheduled = True
            
        self.last_click_time = current_time
        
    def _handle_single_click(self):
        """Handle single click - cycle through statuses"""
        self.single_click_scheduled = False
        
        if self.is_readonly or self.is_future or self._is_future_date():
            return
            
        if not self.habits_model or not self.date_str:
            return
            
        # Get next status in cycle
        next_status = self._get_next_status()
        
        if next_status != self.status:
            old_status = self.status
            
            # Update status in model
            success = self.habits_model.update_habit_status(self.habit_id, self.date_str, next_status)
            
            if success:
                self.status = next_status
                
                # Dispatch events
                self.dispatch('on_status_clicked', self.habit_id, self.date_str, self.status)
                self.dispatch('on_status_changed', self.habit_id, self.date_str, old_status, self.status)
                
    def _handle_double_click(self):
        """Handle double click - show status menu"""
        if self.is_readonly or self.is_future or self._is_future_date():
            return
            
        if not self.habits_model or not self.date_str:
            return
            
        self.dispatch('on_status_double_clicked', self.habit_id, self.date_str, self.status)
        self._show_status_menu()
        
    def _get_next_status(self):
        """Get next status in cycle"""
        if self.habits_model:
            return self.habits_model.get_status_cycle(self.status, self.habit_levels)
        
        # Fallback cycle
        if self.habit_levels == 1:  # Level 1: only basic statuses
            cycle = [0, 2, 9]  # NOT_SET, DONE, FAIL
        elif self.habit_levels == 10:  # Level 10: numeric
            cycle = [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        else:  # Level 3 or 0: full cycle
            cycle = [0, 1, 2, 3, 9]  # NOT_SET, DONE_MINI, DONE, DONE_ELITE, FAIL
            
        try:
            current_index = cycle.index(self.status)
            next_index = (current_index + 1) % len(cycle)
            return cycle[next_index]
        except ValueError:
            return cycle[0]
            
    def _show_status_menu(self):
        """Show status menu popup"""
        try:
            from ..widgets import StatusMenuPopup
            
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
                on_status_selected=self._on_status_selected
            )
            popup.open()
        except ImportError as e:
            Logger.warning(f'UniversalCell: Could not import StatusMenuPopup: {e}')
            
    def _on_status_selected(self, new_status):
        """Handle status selection from popup"""
        if not self.habits_model or not self.date_str:
            return
            
        old_status = self.status
        
        # Update status in model
        success = self.habits_model.update_habit_status(self.habit_id, self.date_str, new_status)
        
        if success:
            self.status = new_status
            self.dispatch('on_status_changed', self.habit_id, self.date_str, old_status, new_status)
            
    # Public API
    def update_status(self, new_status):
        """Update cell status (called externally)"""
        self.status = new_status
        

def create_universal_table(table_data, with_scroll=True, **kwargs):
    """
    Create a universal table widget that can handle any type of cells.
    
    Args:
        table_data: 2D array where each cell can be:
            - str: Simple text (creates label cell)
            - dict: Cell configuration with keys:
                - 'text': Text content
                - 'mode': 'label'|'interactive'|'calendar'
                - 'status': Status value (for interactive/calendar)
                - 'habit_id': Habit ID (for interactive/calendar)
                - 'date_str': Date string (for interactive/calendar)
                - 'day_num': Day number (for calendar)
                - 'habit_levels': Habit levels (for interactive/calendar)
                - 'bad_habit': Bad habit flag (for interactive/calendar)
                - 'habits_model': Habits model reference (for interactive/calendar)
                - 'is_future': Future date flag
                - 'is_readonly': Readonly flag
                - Any other UniversalCell properties
        with_scroll: bool - if True, returns (ScrollView, GridLayout), if False returns (GridLayout, GridLayout)
        
    Returns:
        tuple: (scroll_view, table_grid) if with_scroll=True, (table_grid, table_grid) if with_scroll=False
    """
    if not table_data:
        table_data = [['']]
        
    # Determine columns from first row
    cols = len(table_data[0]) if table_data else 1
    
    # Create GridLayout
    table_grid = GridLayout(
        cols=cols,
        spacing=dp(2),
        size_hint_y=None,
        row_default_height=dp(40),
        row_force_default=True,
    )
    table_grid.bind(minimum_height=table_grid.setter('height'))
    
    # Populate table
    for row_idx, row_data in enumerate(table_data):
        for col_idx, cell_data in enumerate(row_data):
            # Create cell based on data type
            if isinstance(cell_data, dict):
                # Dictionary with cell configuration
                cell = UniversalCell(**cell_data)
            else:
                # Simple text - create label cell
                cell = UniversalCell(
                    cell_mode='label',
                    text=str(cell_data)
                )
            
            table_grid.add_widget(cell)
    
    if with_scroll:
        # Create ScrollView
        scroll = ScrollView(
            bar_width=15,
            bar_color=[0.5, 0.5, 0.5, 0.8],
            bar_inactive_color=[0.7, 0.7, 0.7, 0.4],
            scroll_type=['bars', 'content']
        )
        scroll.add_widget(table_grid)
        return scroll, table_grid
    else:
        # Return table without ScrollView
        return table_grid, table_grid


# Legacy compatibility functions (deprecated)
def create_cell(text="", style=None):
    """Legacy function - use UniversalCell instead"""
    cell = UniversalCell(cell_mode='label', text=str(text))
    if style and isinstance(style, dict) and 'color' in style:
        # Apply color if provided
        pass  # Color is handled by UniversalCell
    return cell
    

def create_table_widget(table_data):
    """Legacy function - use create_universal_table instead"""
    return create_universal_table(table_data)
    

def create_calendar_table(table_data, habit_data=None, habits_model=None):
    """Legacy function - use create_universal_table instead"""
    # Convert legacy format to new format
    if not table_data:
        return create_universal_table([[]])
        
    converted_data = []
    for row_idx, row_data in enumerate(table_data):
        converted_row = []
        for col_idx, cell_data in enumerate(row_data):
            if isinstance(cell_data, dict) and 'day' in cell_data:
                # Interactive calendar cell
                converted_cell = {
                    'cell_mode': 'calendar',
                    'day_num': cell_data.get('day', 0),
                    'status': cell_data.get('status', 0),
                    'date_str': cell_data.get('date', ''),
                    'habit_id': habit_data.get('id', 0) if habit_data else 0,
                    'habit_levels': int(habit_data.get('levels', 0)) if habit_data else 0,
                    'bad_habit': habit_data.get('bad_habit') == '1' if habit_data else False,
                    'habits_model': habits_model
                }
                converted_row.append(converted_cell)
            else:
                # Regular label cell
                converted_row.append(str(cell_data))
        converted_data.append(converted_row)
    
    return create_universal_table(converted_data)
