"""
Universal Table Widget

TRULY universal, project-agnostic table widget.
Contains ONLY basic table functionality: grid with text cells.
NO project-specific logic, NO special modes.
"""

from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.event import EventDispatcher
from typing import Any, Dict, List, Union


class UniversalCell(ButtonBehavior, BoxLayout, EventDispatcher):
    """
    Universal cell widget - JUST A SIMPLE CELL.
    
    Contains ONLY universal functionality:
    - Text display
    - Background color
    - Click events
    - Basic visual states
    
    NO project-specific modes or logic!
    """
    
    # Universal properties - ONLY basic stuff
    text = StringProperty('')
    background_color = ListProperty([1, 1, 1, 1])  # White background
    text_color = ListProperty([0, 0, 0, 1])  # Black text
    is_disabled = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Basic layout setup
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))
        self.padding = dp(2)
        
        # Content widget
        self.label = None
        self.bg_rect = None
        
        # Register universal events
        self.register_event_type('on_cell_clicked')
        
        # Bind properties
        self.bind(text=self._update_text)
        self.bind(background_color=self._update_background)
        self.bind(text_color=self._update_text_color)
        self.bind(is_disabled=self._update_visual_state)
        self.bind(pos=self._update_background_rect)
        self.bind(size=self._update_background_rect)
        
        # Build content
        Clock.schedule_once(lambda dt: self._build_content(), 0)
        
    def _build_content(self):
        """Build simple label content - UNIVERSAL BEHAVIOR"""
        self.label = Label(
            text=self.text,
            size_hint=(1, 1),
            halign="center",
            valign="middle",
            color=self.text_color
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)
        
        # Draw background
        self._update_background()
        
    def _update_text(self, *args):
        """Update text - UNIVERSAL BEHAVIOR"""
        if self.label:
            self.label.text = self.text
            
    def _update_text_color(self, *args):
        """Update text color - UNIVERSAL BEHAVIOR"""
        if self.label:
            self.label.color = self.text_color
            
    def _update_background(self, *args):
        """Update background color - UNIVERSAL BEHAVIOR"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            
    def _update_background_rect(self, *args):
        """Update background rectangle - UNIVERSAL BEHAVIOR"""
        if hasattr(self, 'bg_rect') and self.bg_rect:
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
            
    def _update_visual_state(self, *args):
        """Update visual state - UNIVERSAL BEHAVIOR"""
        if self.is_disabled:
            self.opacity = 0.5
            self.disabled = True
        else:
            self.opacity = 1.0
            self.disabled = False
            
    # Universal event handling
    def on_cell_clicked(self, cell):
        """Universal click event"""
        pass
        
    def on_press(self):
        """Handle button press - UNIVERSAL BEHAVIOR"""
        if self.is_disabled:
            return
            
        self.dispatch('on_cell_clicked', self)


def create_universal_table(
    table_data: List[List[Union[str, Dict[str, Any]]]], 
    with_scroll: bool = True,
    cell_class: type = UniversalCell,
    **kwargs
) -> tuple:
    """
    Create a universal table widget - JUST A GRID WITH CELLS.
    
    Args:
        table_data: 2D array where each cell can be:
            - str: Simple text
            - dict: Cell configuration with universal properties:
                - 'text': Text content
                - 'background_color': Background color
                - 'text_color': Text color
                - 'is_disabled': Disabled state
        with_scroll: bool - if True, wraps table in ScrollView
        cell_class: Cell class to use (UniversalCell or subclass)
        **kwargs: Additional arguments for GridLayout
        
    Returns:
        tuple: (container, table_grid)
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
        **kwargs
    )
    table_grid.bind(minimum_height=table_grid.setter('height'))
    
    # Populate table
    for row_data in table_data:
        for cell_data in row_data:
            # Create cell based on data type
            if isinstance(cell_data, dict):
                # Pass all properties if using custom cell class
                if cell_class != UniversalCell:
                    # Pass all properties to custom cell class
                    cell = cell_class(**cell_data)
                else:
                    # Filter only universal properties for UniversalCell
                    universal_props = {
                        k: v for k, v in cell_data.items() 
                        if k in ['text', 'background_color', 'text_color', 'is_disabled']
                    }
                    cell = cell_class(**universal_props)
            else:
                # Simple text cell
                cell = cell_class(text=str(cell_data))
            
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
        return table_grid, table_grid


class SimpleTable:
    """
    Simple table builder for quick table creation - UNIVERSAL ONLY
    """
    
    def __init__(self, cell_class: type = UniversalCell):
        self.cell_class = cell_class
        self.rows = []
        
    def add_row(self, row_data: List[Union[str, Dict[str, Any]]]):
        """Add a row to the table"""
        self.rows.append(row_data)
        
    def add_header_row(self, headers: List[str]):
        """Add a header row"""
        header_row = [{'text': str(h), 'background_color': [0.9, 0.9, 0.9, 1]} for h in headers]
        self.rows.append(header_row)
        
    def build(self, with_scroll: bool = True, **kwargs):
        """Build and return the table"""
        return create_universal_table(
            self.rows, 
            with_scroll=with_scroll, 
            cell_class=self.cell_class,
            **kwargs
        )
        
    def clear(self):
        """Clear all rows"""
        self.rows.clear() 