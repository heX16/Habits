"""
Habits Table Widget

Extends the universal table widget with ALL habits-specific functionality.
Contains ALL project-specific logic that was removed from universal_table.py:
- Cell modes (interactive, calendar)
- Double-click detection
- Status management
- Icons and colors
- Integration with HabitsModel
"""

from .universal_table import UniversalCell, create_universal_table
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import (
    NumericProperty, BooleanProperty, ObjectProperty, StringProperty
)
from datetime import date, datetime
import os
from typing import Any, Dict, List, Optional, Union


class HabitsCell(UniversalCell):
    """
    Habits-specific cell that extends UniversalCell with ALL project-specific functionality.
    
    This class contains ALL habits-specific logic:
    - Cell modes: 'interactive', 'calendar' 
    - Double-click detection
    - Status management and cycling
    - Status icons, colors, and display
    - Integration with HabitsModel
    """
    
    # Habits-specific properties
    cell_mode = StringProperty('label')  # 'label', 'interactive', 'calendar'
    habit_id = NumericProperty(0)
    date_str = StringProperty('')
    habit_levels = NumericProperty(0)  # 0=all, 1=limited, 3=basic, 10=numeric
    bad_habit = BooleanProperty(False)
    day_num = NumericProperty(0)  # For calendar cells
    value = NumericProperty(0)  # Status value
    identifier = StringProperty('')  # Generic identifier
    is_dimmed = BooleanProperty(False)
    
    # Model reference
    habits_model = ObjectProperty(None, allownone=True)
    
    # Habits-specific status constants
    STATUS_NOT_SET = 0
    STATUS_DONE_MINI = 1
    STATUS_DONE = 2
    STATUS_DONE_ELITE = 3
    STATUS_FAIL = 9
    STATUS_NUMERIC_START = 10
    STATUS_NUMERIC_END = 19
    
    def __init__(self, **kwargs):
        # Handle habits-specific initialization
        if 'status' in kwargs:
            kwargs['value'] = kwargs.pop('status')
        if 'habit_id' in kwargs:
            kwargs['identifier'] = str(kwargs['habit_id'])
            
        # Double-click detection
        self.last_click_time = 0
        self.double_click_timeout = 0.3
        self.single_click_scheduled = False
        
        # Content widgets storage
        self.content_widgets = []
        
        super().__init__(**kwargs)
        
        # Register habits events
        self.register_event_type('on_cell_double_clicked')
        self.register_event_type('on_cell_value_changed')
        
        # Set up habits-specific bindings
        self.bind(habit_id=self._sync_identifier)
        self.bind(value=self._sync_status)
        self.bind(cell_mode=self._rebuild_cell)
        self.bind(day_num=self._rebuild_cell)
        self.bind(is_dimmed=self._update_visual_state)
        
        # Override the build to handle modes
        self.unbind(text=self._update_text)  # Remove universal text binding
        
        # Update future date state
        self._update_future_state()
        
    def _sync_identifier(self, instance, value):
        """Sync habit_id with universal identifier"""
        self.identifier = str(value)
        
    def _sync_status(self, instance, value):
        """Handle status changes"""
        self._update_future_state()
        # Trigger visual update when value changes
        self._rebuild_cell()
        
    def _update_future_state(self):
        """Update future date state - habits-specific logic"""
        if self.date_str:
            self.is_dimmed = self._is_future_date()
            
    def _is_future_date(self):
        """Check if date is in future - habits-specific logic"""
        if not self.date_str:
            return False
            
        try:
            cell_date = datetime.strptime(self.date_str, '%Y-%m-%d').date()
            return cell_date > date.today()
        except ValueError:
            return False
            
    def _build_content(self):
        """Override to handle different cell modes"""
        if self.cell_mode == 'label':
            # Use parent's simple label build
            super()._build_content()
        else:
            # Build habits-specific content directly
            self._rebuild_cell()
            
    def _rebuild_cell(self, *args):
        """Rebuild cell content based on mode"""
        # Clear existing content first
        self.clear_widgets()
        self.content_widgets.clear()
        
        if self.cell_mode == 'interactive':
            self._build_interactive_content()
        elif self.cell_mode == 'calendar':
            self._build_calendar_content()
        elif self.cell_mode == 'label':
            # Use universal label build
            super()._build_content()
            return
        
        # Update visual state after building content
        self._update_visual_state()
            
    def _build_interactive_content(self):
        """Build habits-specific interactive content"""
        if self.value == self.STATUS_NOT_SET:
            # Empty cell - still add a label for clicking
            content = Label(
                text='', 
                size_hint=(1, 1), 
                halign="center", 
                valign="middle",
                color=self.text_color
            )
            content.bind(size=content.setter('text_size'))
            self.add_widget(content)
            self.content_widgets.append(content)
        elif self.STATUS_NUMERIC_START <= self.value <= self.STATUS_NUMERIC_END:
            # Numeric display (0-9)
            content = Label(
                text=str(self.value - self.STATUS_NUMERIC_START),
                size_hint=(1, 1),
                halign="center",
                valign="middle",
                color=self.text_color
            )
            content.bind(size=content.setter('text_size'))
            self.add_widget(content)
            self.content_widgets.append(content)
        else:
            # Status icon or emoji
            self._build_status_display((1, 1))
            
        # Update background color
        self.background_color = self._get_status_color()
            
    def _build_calendar_content(self):
        """Build habits-specific calendar content"""
        if self.day_num > 0:
            # Day number
            day_label = Label(
                text=str(self.day_num),
                font_size='12sp',
                size_hint=(1, 0.6),
                halign="center",
                valign="middle",
                color=self.text_color
            )
            day_label.bind(size=day_label.setter('text_size'))
            self.add_widget(day_label)
            self.content_widgets.append(day_label)
            
            # Status display
            if self.value != self.STATUS_NOT_SET:
                if self.STATUS_NUMERIC_START <= self.value <= self.STATUS_NUMERIC_END:
                    content = Label(
                        text=str(self.value - self.STATUS_NUMERIC_START),
                        font_size='10sp',
                        size_hint=(1, 0.4),
                        halign="center",
                        valign="middle",
                        color=self.text_color
                    )
                    content.bind(size=content.setter('text_size'))
                    self.add_widget(content)
                    self.content_widgets.append(content)
                else:
                    self._build_status_display((1, 0.4))
                    
        # Update background color
        self.background_color = self._get_status_color()
                    
    def _build_status_display(self, size_hint):
        """Build status display (icon or emoji) - habits-specific logic"""
        icon_path = self._get_status_icon_path()
        if icon_path and os.path.exists(icon_path):
            # Use icon
            content = Image(
                source=icon_path,
                size_hint=size_hint,
                allow_stretch=True,
                keep_ratio=True
            )
            self.add_widget(content)
            self.content_widgets.append(content)
        else:
            # Use emoji fallback
            content = Label(
                text=self._get_status_emoji(),
                size_hint=size_hint,
                halign="center",
                valign="middle",
                color=self.text_color
            )
            content.bind(size=content.setter('text_size'))
            self.add_widget(content)
            self.content_widgets.append(content)
            
    def _update_content(self):
        """Update habits-specific content - simplified version"""
        # Just rebuild the cell when content needs updating
        self._rebuild_cell()
        
    def _get_status_icon_path(self):
        """Get icon path for status - habits-specific logic"""
        icon_map = {
            self.STATUS_DONE_MINI: 'app/assets/images/done_mini.png',
            self.STATUS_DONE: 'app/assets/images/done.png',
            self.STATUS_DONE_ELITE: 'app/assets/images/done_elite.png',
            self.STATUS_FAIL: 'app/assets/images/fail.png',
        }
        return icon_map.get(self.value, '')
        
    def _get_status_emoji(self):
        """Get emoji for status - habits-specific logic"""
        emoji_map = {
            self.STATUS_DONE_MINI: '✓',
            self.STATUS_DONE: '✓✓',
            self.STATUS_DONE_ELITE: '★',
            self.STATUS_FAIL: '✗',
        }
        return emoji_map.get(self.value, '')
        
    def _get_status_color(self):
        """Get background color for status - habits-specific logic"""
        if self.value == self.STATUS_NOT_SET:
            return [1, 1, 1, 1]  # White
        elif self.value == self.STATUS_DONE_MINI:
            return [0.8, 1, 0.8, 1] if not self.bad_habit else [1, 0.8, 0.8, 1]
        elif self.value == self.STATUS_DONE:
            return [0.6, 1, 0.6, 1] if not self.bad_habit else [1, 0.6, 0.6, 1]
        elif self.value == self.STATUS_DONE_ELITE:
            return [0.4, 1, 0.4, 1] if not self.bad_habit else [1, 0.4, 0.4, 1]
        elif self.value == self.STATUS_FAIL:
            return [1, 0.6, 0.6, 1] if not self.bad_habit else [0.6, 1, 0.6, 1]
        elif self.STATUS_NUMERIC_START <= self.value <= self.STATUS_NUMERIC_END:
            if self.value == self.STATUS_NUMERIC_START:  # 0
                return [0.8, 0.8, 1, 1]  # Blue
            else:
                return [1, 0.8, 0.8, 1] if not self.bad_habit else [0.8, 1, 0.8, 1]
        else:
            return [1, 1, 1, 1]  # White for unknown
            
    def _update_visual_state(self, *args):
        """Update visual state - habits-specific logic"""
        # Update background color based on status
        if self.cell_mode != 'label':
            self.background_color = self._get_status_color()
            
            # Apply dimming for future dates
            if self.is_dimmed:
                # Make background slightly transparent for future dates
                color = [float(c) for c in self.background_color]
                if len(color) >= 4:
                    color[3] = 0.5  # Reduce alpha
                self.background_color = color
            
    # Override click handling for double-click support
    def on_press(self):
        """Handle button press with double-click detection"""
        if self.cell_mode == 'label' or self.is_disabled:
            return
            
        current_time = Clock.get_time()
        
        # Double-click detection
        if current_time - self.last_click_time < self.double_click_timeout:
            self._handle_double_click()
            if self.single_click_scheduled:
                Clock.unschedule(self._handle_single_click)
                self.single_click_scheduled = False
        else:
            Clock.schedule_once(lambda dt: self._handle_single_click(), self.double_click_timeout)
            self.single_click_scheduled = True
            
        self.last_click_time = current_time
        
    def _handle_single_click(self):
        """Handle single click - habits-specific status cycling"""
        self.single_click_scheduled = False
        
        if self.is_disabled or self.is_dimmed or self._is_future_date():
            return
            
        if not self.habits_model or not self.date_str:
            return
            
        # Get next status in cycle
        next_status = self._get_next_status()
        
        if next_status != self.value:
            old_value = self.value
            
            # Update status in model
            success = self.habits_model.update_habit_status(self.habit_id, self.date_str, next_status)
            
            if success:
                self.value = next_status
                self.dispatch('on_cell_value_changed', self, self.identifier, old_value, self.value)
                
        # Also dispatch base event
        self.dispatch('on_cell_clicked', self)
        
    def _handle_double_click(self):
        """Handle double click - habits-specific status menu"""
        if self.is_disabled or self.is_dimmed or self._is_future_date():
            return
            
        if not self.habits_model or not self.date_str:
            return
            
        self.dispatch('on_cell_double_clicked', self, self.identifier, self.value)
        self._show_status_menu()
        
    def _get_next_status(self):
        """Get next status in cycle - habits-specific logic"""
        if self.habits_model:
            next_status = self.habits_model.get_status_cycle(self.value, self.habit_levels)
            if hasattr(next_status, 'value'):
                return next_status.value
            return int(next_status)
        
        # Fallback cycle logic
        if self.habit_levels == 1:  # Level 1: basic
            cycle = [self.STATUS_NOT_SET, self.STATUS_DONE, self.STATUS_FAIL]
        elif self.habit_levels == 10:  # Level 10: numeric
            cycle = list(range(self.STATUS_NOT_SET, self.STATUS_NUMERIC_END + 1))
        else:  # Level 3 or 0: full
            cycle = [
                self.STATUS_NOT_SET, 
                self.STATUS_DONE_MINI, 
                self.STATUS_DONE, 
                self.STATUS_DONE_ELITE, 
                self.STATUS_FAIL
            ]
            
        try:
            current_index = cycle.index(self.value)
            next_index = (current_index + 1) % len(cycle)
            return cycle[next_index]
        except ValueError:
            return cycle[0]
            
    def _show_status_menu(self):
        """Show status menu - habits-specific logic"""
        try:
            from . import StatusMenuPopup
            
            habit_data = {
                'name': f'Habit {self.habit_id}',
                'levels': self.habit_levels,
                'bad_habit': '1' if self.bad_habit else '0',
                'mode': f'level{self.habit_levels}' if self.habit_levels in [1, 10] else 'level3'
            }
            
            popup = StatusMenuPopup(
                habit_data=habit_data,
                current_status=self.value,
                on_status_selected=self._on_status_selected
            )
            popup.open()
        except ImportError as e:
            Logger.warning(f'HabitsCell: Could not import StatusMenuPopup: {e}')
            
    def _on_status_selected(self, new_status):
        """Handle status selection - habits-specific logic"""
        if not self.habits_model or not self.date_str:
            return
            
        old_value = self.value
        
        success = self.habits_model.update_habit_status(self.habit_id, self.date_str, new_status)
        
        if success:
            self.value = new_status
            self.dispatch('on_cell_value_changed', self, self.identifier, old_value, new_status)
            
    # Events
    def on_cell_double_clicked(self, cell, identifier: str, value: Any):
        """Event for double click"""
        pass
        
    def on_cell_value_changed(self, cell, identifier: str, old_value: Any, new_value: Any):
        """Event for value change"""
        pass
        
    # Compatibility properties
    @property
    def status(self):
        """Compatibility property for status"""
        return self.value
        
    @status.setter
    def status(self, value):
        """Compatibility property for status"""
        self.value = value
        
    def update_status(self, new_status):
        """Compatibility method for status updates"""
        self.value = new_status


# Habits-specific table creation functions
def create_habits_table(table_data: List[List[Union[str, Dict[str, Any]]]], 
                       with_scroll: bool = True, 
                       **kwargs) -> tuple:
    """
    Create a habits-specific table widget.
    """
    return create_universal_table(
        table_data, 
        with_scroll=with_scroll, 
        cell_class=HabitsCell,
        **kwargs
    )


def create_habits_main_table(habits_data: List[Dict], dates: List[str], 
                            habits_model, **kwargs) -> tuple:
    """
    Create the main habits tracker table - habits-specific logic.
    """
    table_data = []
    
    # Header row
    header_row = ['Habit']
    for date_str in dates:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            header_row.append(f"{date_obj.strftime('%a')}\n{date_obj.day}")
        except ValueError:
            header_row.append(date_str)
    table_data.append(header_row)
    
    # Data rows
    for habit in habits_data:
        row = [habit['name']]
        
        for date_str in dates:
            status = habits_model.get_habit_status(habit['id'], date_str)
            
            cell_config = {
                'cell_mode': 'interactive',
                'value': status,
                'habit_id': habit['id'],
                'date_str': date_str,
                'habit_levels': int(habit.get('levels', 0)),
                'bad_habit': habit.get('bad_habit') == '1',
                'habits_model': habits_model
            }
            row.append(cell_config)
        
        table_data.append(row)
    
    return create_habits_table(table_data, **kwargs)


def create_habits_calendar_table(habit_data: Dict, month_data: List[List[Dict]], 
                                habits_model, **kwargs) -> tuple:
    """
    Create a habits calendar table - habits-specific logic.
    """
    table_data = []
    
    # Header row
    header_row = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    table_data.append(header_row)
    
    # Data rows
    for week in month_data:
        row = []
        for day_data in week:
            if day_data.get('day', 0) > 0:
                cell_config = {
                    'cell_mode': 'calendar',
                    'day_num': day_data['day'],
                    'value': day_data.get('status', 0),
                    'habit_id': habit_data['id'],
                    'date_str': day_data.get('date', ''),
                    'habit_levels': int(habit_data.get('levels', 0)),
                    'bad_habit': habit_data.get('bad_habit') == '1',
                    'habits_model': habits_model
                }
                row.append(cell_config)
            else:
                row.append('')
        table_data.append(row)
    
    return create_habits_table(table_data, **kwargs) 