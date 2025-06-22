"""
Status Cell Widget

Interactive cell widget for displaying and editing habit status.
Handles single-click cycling, double-click menu, and visual feedback.
"""

from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.event import EventDispatcher

from common_lib.habits_database import HabitStatus


class StatusCell(ButtonBehavior, BoxLayout, EventDispatcher):
    """
    Interactive cell for displaying and editing habit status.
    Supports single-click cycling and double-click menu.
    """
    
    # Properties for data binding
    habit_id = NumericProperty(0)
    date_str = StringProperty('')
    status = NumericProperty(0)
    habit_levels = NumericProperty(0)  # 0=all, 1=limited, 3=basic
    is_future = BooleanProperty(False)
    is_readonly = BooleanProperty(False)
    
    # Visual properties
    cell_size = NumericProperty(50)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set up the layout
        self.orientation = 'horizontal'
        self.spacing = 0
        self.size_hint = (None, None)
        self.size = (self.cell_size, self.cell_size)
        
        # Double-click detection
        self.last_click_time = 0
        self.double_click_timeout = 0.3
        
        # Create content widgets
        self.image_widget = Image(
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        self.text_widget = Label(
            size_hint=(1, 1),
            text='',
            font_size=16,
            halign='center',
            valign='middle'
        )
        
        # Add widgets to layout
        self.add_widget(self.image_widget)
        self.add_widget(self.text_widget)
        
        # Register events
        self.register_event_type('on_status_clicked')
        self.register_event_type('on_status_double_clicked')
        self.register_event_type('on_status_changed')
        
        # Bind property changes
        self.bind(status=self.update_display)
        self.bind(is_future=self.update_display)
        self.bind(is_readonly=self.update_display)
        
        # Initial display update
        Clock.schedule_once(lambda dt: self.update_display(), 0)
        
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
        """Handle button press (touch down)"""
        current_time = Clock.get_time()
        
        # Check if it's a double-click
        if current_time - self.last_click_time < self.double_click_timeout:
            self.handle_double_click()
        else:
            # Schedule single click handling (to allow for double-click detection)
            Clock.schedule_once(lambda dt: self.handle_single_click(), self.double_click_timeout)
            
        self.last_click_time = current_time
        
    def handle_single_click(self):
        """Handle single click - cycle through statuses"""
        # Check if click is still valid (no double-click occurred)
        if Clock.get_time() - self.last_click_time >= self.double_click_timeout:
            return
            
        if self.is_readonly or self.is_future:
            Logger.info(f'StatusCell: Click ignored - readonly={self.is_readonly}, future={self.is_future}')
            return
            
        Logger.info(f'StatusCell: Single click on habit {self.habit_id}, date {self.date_str}, status {self.status}')
        
        # Cycle to next status
        next_status = self.get_next_status_in_cycle()
        
        if next_status != self.status:
            old_status = self.status
            self.status = next_status
            
            # Dispatch events
            self.dispatch('on_status_clicked', self.habit_id, self.date_str, self.status)
            self.dispatch('on_status_changed', self.habit_id, self.date_str, old_status, self.status)
            
    def handle_double_click(self):
        """Handle double click - show status menu"""
        if self.is_readonly or self.is_future:
            Logger.info(f'StatusCell: Double-click ignored - readonly={self.is_readonly}, future={self.is_future}')
            return
            
        Logger.info(f'StatusCell: Double click on habit {self.habit_id}, date {self.date_str}')
        self.dispatch('on_status_double_clicked', self.habit_id, self.date_str, self.status)
        
    def get_next_status_in_cycle(self) -> int:
        """Get the next status in the cycling sequence"""
        # Standard cycle: 0 → 1 → 2 → 3 → 9 → 0
        if self.habit_levels == 1:  # Level 1: only basic statuses
            cycle = [HabitStatus.NOT_SET, HabitStatus.DONE, HabitStatus.FAIL]
        else:  # Level 3 or 0: full cycle
            cycle = [
                HabitStatus.NOT_SET,
                HabitStatus.DONE_MINI,
                HabitStatus.DONE,
                HabitStatus.DONE_ELITE,
                HabitStatus.FAIL
            ]
            
        try:
            current_index = cycle.index(self.status)
            next_index = (current_index + 1) % len(cycle)
            return cycle[next_index]
        except ValueError:
            # If current status is not in cycle, return first status
            return cycle[0]
            
    def update_display(self, *args):
        """Update the visual display based on current status"""
        # Clear both widgets first
        self.image_widget.source = ''
        self.text_widget.text = ''
        
        # Apply visual state for future/readonly
        if self.is_future:
            self.opacity = 0.5
            self.disabled = True
        elif self.is_readonly:
            self.opacity = 0.8
            self.disabled = True
        else:
            self.opacity = 1.0
            self.disabled = False
            
        # Set content based on status
        if self.status == HabitStatus.NOT_SET:
            # Empty cell
            pass
        elif 10 <= self.status <= 19:
            # Numeric status (0-9)
            self.text_widget.text = str(self.status - 10)
        else:
            # Icon-based status
            icon_path = self.get_status_icon_path()
            if icon_path:
                self.image_widget.source = icon_path
                
        # Update background color based on status
        self.update_background_color()
        
    def get_status_icon_path(self) -> str:
        """Get the icon path for the current status"""
        icon_map = {
            HabitStatus.DONE_MINI: 'app/assets/images/done_mini.png',
            HabitStatus.DONE: 'app/assets/images/done.png',
            HabitStatus.DONE_ELITE: 'app/assets/images/done_elite.png',
            HabitStatus.FAIL: 'app/assets/images/fail.png',
        }
        return icon_map.get(self.status, '')
        
    def update_background_color(self):
        """Update background color based on status and state"""
        # Base colors for different statuses
        color_map = {
            HabitStatus.NOT_SET: (0.95, 0.95, 0.95, 1),  # Light gray
            HabitStatus.DONE_MINI: (0.8, 0.9, 1, 1),     # Light blue
            HabitStatus.DONE: (0.8, 1, 0.8, 1),          # Light green
            HabitStatus.DONE_ELITE: (1, 0.9, 0.8, 1),    # Light orange
            HabitStatus.FAIL: (1, 0.8, 0.8, 1),          # Light red
        }
        
        # Default color for numeric statuses
        if 10 <= self.status <= 19:
            base_color = (0.9, 0.9, 1, 1)  # Light purple
        else:
            base_color = color_map.get(self.status, (0.95, 0.95, 0.95, 1))
            
        # Modify color based on state
        if self.is_future:
            # Darken for future dates
            color = tuple(c * 0.7 if i < 3 else c for i, c in enumerate(base_color))
        elif self.is_readonly:
            # Slightly darken for readonly
            color = tuple(c * 0.9 if i < 3 else c for i, c in enumerate(base_color))
        else:
            color = base_color
            
        # Apply color (this would need to be implemented with canvas instructions)
        # For now, we'll use the button's background_color property
        if hasattr(self, 'background_color'):
            self.background_color = color
            
    def set_status(self, new_status: int, update_display: bool = True):
        """
        Set the status programmatically.
        
        :param new_status: New status value
        :param update_display: Whether to update the display immediately
        """
        old_status = self.status
        self.status = new_status
        
        if update_display:
            self.update_display()
            
        if old_status != new_status:
            self.dispatch('on_status_changed', self.habit_id, self.date_str, old_status, new_status) 