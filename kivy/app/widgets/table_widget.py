"""
Table Widget Utilities

Provides functions for creating and managing table widgets with ScrollView and GridLayout.
Extracted from main.py for clean imports and better code organization.
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
from datetime import date, datetime


def create_cell(text="", style=None):
    """Creates a standardized cell widget (Label) with given text and style"""
    label = Label(
        text=str(text),
        size_hint_y=None,
        height=dp(40),
        halign="center",
        valign="middle"
    )
    label.bind(size=label.setter('text_size'))  

    # Apply style if provided
    if style and isinstance(style, dict):
        if 'color' in style and style['color'] is not None:
            # Convert color to RGBA format if needed
            color = style['color']
            if isinstance(color, (list, tuple)) and len(color) >= 3:
                label.color = color

    return label


def create_table_widget(table_data):
    """Creates a table widget (ScrollView + GridLayout)"""
    # Determine the number of columns from the first row (headers)
    cols = len(table_data[0]) if table_data else 1

    # Create ScrollView with table
    scroll = ScrollView(
        bar_width=15,  # Make the scrollbar wider (default is 2)
        bar_color=[0.5, 0.5, 0.5, 0.8],  # Gray color for active bar
        bar_inactive_color=[0.7, 0.7, 0.7, 0.4],  # Light gray for inactive
        scroll_type=['bars', 'content']  # Can scroll both by bar and by content
    )

    # Create GridLayout for the table
    table_grid = GridLayout(
        cols=cols,
        spacing=dp(1),
        size_hint_y=None,
        row_default_height=dp(40),
        row_force_default=True,
    )
    # Bind height to minimum height for scrolling
    table_grid.bind(minimum_height=table_grid.setter('height'))  

    scroll.add_widget(table_grid)
    return scroll, table_grid


def recreate_table(table_grid, table_data, table_style=None):
    """Updates the entire table based on table_data and table_style using create_cell for direct creation"""
    if not table_grid or not table_data:
        return

    # Clear the table
    table_grid.clear_widgets()

    # Create all widgets directly with their text and style using create_cell function
    for row_idx, row in enumerate(table_data):
        for col_idx, cell in enumerate(row):
            # Get style for this cell
            cell_style = None
            if table_style and row_idx < len(table_style) and col_idx < len(table_style[row_idx]):
                cell_style = table_style[row_idx][col_idx]

            label = create_cell(cell, cell_style)  # Create with actual text and style
            table_grid.add_widget(label)


def update_table(table_grid, table_data, table_style=None):
    """Updates table content without recreating widgets"""
    if not table_grid or not table_data:
        return False

    cols = table_grid.cols
    rows = len(table_data)
    total_widgets = len(table_grid.children)
    expected_widgets = rows * cols

    # Check that the number of widgets matches expected
    if total_widgets != expected_widgets:
        print(f"Warning: Expected {expected_widgets} widgets, but found {total_widgets}")
        return False

    # Check that all rows have the correct number of columns
    for i, row in enumerate(table_data):
        if len(row) != cols:
            print(f"Error: Row {i} has {len(row)} columns, but table has {cols} columns")
            return False

    # Update the content of each widget
    for row in range(rows):
        for col in range(cols):
            # Calculate widget index in children (reverse order)
            widget_idx = total_widgets - 1 - (row * cols + col)

            if 0 <= widget_idx < len(table_grid.children):
                widget = table_grid.children[widget_idx]
                new_text = str(table_data[row][col])

                # Get style for this cell
                cell_style = None
                if table_style and row < len(table_style) and col < len(table_style[row]):
                    cell_style = table_style[row][col]

                # Update text only if it has changed
                if hasattr(widget, 'text') and widget.text != new_text:
                    widget.text = new_text

                # Apply style
                if cell_style and isinstance(cell_style, dict):
                    if 'color' in cell_style and cell_style['color'] is not None:
                        color = cell_style['color']
                        if isinstance(color, (list, tuple)) and len(color) >= 3:
                            widget.color = color

    return True


class InteractiveCalendarCell(ButtonBehavior, BoxLayout):
    """Interactive calendar cell for habit tracking"""
    
    def __init__(self, day_num=0, status=0, date_str='', habit_id=0, habit_levels=0, bad_habit=False, habits_model=None, **kwargs):
        super().__init__(**kwargs)
        
        self.day_num = day_num
        self.status = status
        self.date_str = date_str
        self.habit_id = habit_id
        self.habit_levels = habit_levels
        self.bad_habit = bad_habit
        self.habits_model = habits_model
        
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
        
        try:
            return icon_map.get(HabitStatus(self.status))
        except (ValueError, ImportError):
            return None
        
    def _update_background(self):
        """Update background color based on status"""
        try:
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
        except ImportError:
            bg_color = (0.95, 0.95, 0.95, 1)
        
        # Check if date is in the future
        if self.date_str and self._is_future_date():
            bg_color = (0.9, 0.9, 0.9, 1)  # Gray for future dates
        
        with self.canvas.before:
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
                on_status_selected=self._on_status_changed
            )
            popup.open()
        except ImportError as e:
            Logger.warning(f'InteractiveCalendarCell: Could not import StatusMenuPopup: {e}')
        
    def _on_status_changed(self, new_status):
        """Handle status change from popup"""
        if not self.habits_model or not self.date_str:
            return
            
        # Update status in model
        success = self.habits_model.update_habit_status(self.habit_id, self.date_str, new_status)
        
        if success:
            self.status = new_status
            self._build_cell()
    
    def update_status(self, new_status):
        """Update cell status (called externally)"""
        self.status = new_status
        self._build_cell()


def create_calendar_table(table_data, habit_data=None, habits_model=None):
    """
    Creates a calendar table widget with interactive cells
    
    Args:
        table_data: 2D array of calendar data [row][col] = {'day': int, 'status': int, 'date': str}
        habit_data: Dict with habit information (id, levels, bad_habit)
        habits_model: Reference to habits model for status updates
    
    Returns:
        tuple: (scroll_view, table_grid)
    """
    if not table_data:
        return create_table_widget([[]])
    
    # Determine the number of columns from the first row
    cols = len(table_data[0]) if table_data else 8  # Default to 8 (Week + 7 days)
    
    # Create ScrollView with table
    scroll = ScrollView(
        bar_width=15,
        bar_color=[0.5, 0.5, 0.5, 0.8],
        bar_inactive_color=[0.7, 0.7, 0.7, 0.4],
        scroll_type=['bars', 'content']
    )
    
    # Create GridLayout for the calendar table
    table_grid = GridLayout(
        cols=cols,
        spacing=dp(2),
        size_hint_y=None,
        row_default_height=dp(40),
        row_force_default=True,
    )
    table_grid.bind(minimum_height=table_grid.setter('height'))
    
    # Populate the table
    for row_idx, row_data in enumerate(table_data):
        for col_idx, cell_data in enumerate(row_data):
            if isinstance(cell_data, dict) and 'day' in cell_data:
                # Interactive calendar cell
                cell = InteractiveCalendarCell(
                    day_num=cell_data.get('day', 0),
                    status=cell_data.get('status', 0),
                    date_str=cell_data.get('date', ''),
                    habit_id=habit_data.get('id', 0) if habit_data else 0,
                    habit_levels=int(habit_data.get('levels', 0)) if habit_data else 0,
                    bad_habit=habit_data.get('bad_habit') == '1' if habit_data else False,
                    habits_model=habits_model
                )
                table_grid.add_widget(cell)
            else:
                # Regular label cell (headers, week numbers, etc.)
                cell = create_cell(str(cell_data))
                table_grid.add_widget(cell)
    
    scroll.add_widget(table_grid)
    return scroll, table_grid


def update_cell(table_grid, table_data, row, col, text, style=None):
    """Updates a specific cell in both data and widget with optional style"""
    if not (0 <= row < len(table_data) and 0 <= col < len(table_data[row])):
        print(f"Error: Invalid cell position ({row}, {col})")
        return False

    # Update data
    table_data[row][col] = str(text)

    # Update corresponding widget if table_grid is provided
    if table_grid:
        cols = table_grid.cols
        total_widgets = len(table_grid.children)

        # Calculate widget index (widgets are in reverse order)
        widget_idx = total_widgets - 1 - (row * cols + col)

        if 0 <= widget_idx < len(table_grid.children):
            widget = table_grid.children[widget_idx]
            if hasattr(widget, 'text'):
                widget.text = str(text)

            # Apply style if provided
            if style and isinstance(style, dict):
                if 'color' in style and style['color'] is not None:
                    # Convert color to RGBA format if needed
                    color = style['color']
                    if isinstance(color, (list, tuple)) and len(color) >= 3:
                        widget.color = color

    return True
