"""
Habit Row Widget

Widget representing a complete row in the habits table.
Contains habit name and status cells for each date.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.properties import NumericProperty, StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.event import EventDispatcher

from .table_widget import UniversalCell


class HabitRow(BoxLayout, EventDispatcher):
    """
    Complete row widget for a habit with status cells.
    """
    
    # Properties for data binding
    habit_id = NumericProperty(0)
    habit_name = StringProperty('')
    habit_levels = NumericProperty(0)
    dates_data = ListProperty([])
    is_readonly = BooleanProperty(False)
    
    # Visual properties
    row_height = NumericProperty(50)
    name_width = NumericProperty(200)
    cell_size = NumericProperty(50)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set up the layout
        self.orientation = 'horizontal'
        self.spacing = 2
        self.size_hint = (None, None)
        self.height = self.row_height
        
        # Create habit name label
        self.name_label = Label(
            text=self.habit_name,
            size_hint=(None, 1),
            width=self.name_width,
            text_size=(self.name_width - 10, None),
            halign='left',
            valign='middle',
            font_size=14
        )
        self.add_widget(self.name_label)
        
        # Container for status cells
        self.cells_container = BoxLayout(
            orientation='horizontal',
            size_hint=(None, 1),
            spacing=1
        )
        self.add_widget(self.cells_container)
        
        # List to keep track of status cells
        self.status_cells = []
        
        # Register events
        self.register_event_type('on_status_clicked')
        self.register_event_type('on_status_double_clicked')
        self.register_event_type('on_status_changed')
        
        # Bind property changes
        self.bind(habit_name=self.update_name_label)
        self.bind(dates_data=self.rebuild_cells)
        self.bind(is_readonly=self.update_cells_readonly)
        
    def on_status_clicked(self, habit_id: int, date_str: str, status: int):
        """Event for status cell clicked"""
        pass
        
    def on_status_double_clicked(self, habit_id: int, date_str: str, status: int):
        """Event for status cell double-clicked"""
        pass
        
    def on_status_changed(self, habit_id: int, date_str: str, old_status: int, new_status: int):
        """Event for status changed"""
        pass
        
    def update_name_label(self, *args):
        """Update the habit name label"""
        self.name_label.text = self.habit_name
        
    def update_cells_readonly(self, *args):
        """Update readonly state for all cells"""
        for cell in self.status_cells:
            cell.is_readonly = self.is_readonly
            
    def rebuild_cells(self, *args):
        """Rebuild status cells based on dates_data"""
        Logger.info(f'HabitRow: Rebuilding cells for habit {self.habit_id} with {len(self.dates_data)} dates')
        
        # Clear existing cells
        self.cells_container.clear_widgets()
        self.status_cells.clear()
        
        # Create new cells for each date
        total_width = 0
        for date_info in self.dates_data:
            cell = UniversalCell(
                cell_mode='interactive',
                habit_id=self.habit_id,
                date_str=date_info['date'],
                status=date_info.get('status', 0),
                habit_levels=self.habit_levels,
                is_future=date_info.get('is_future', False),
                is_readonly=self.is_readonly,
                size=(self.cell_size, self.cell_size)
            )
            
            # Bind cell events to row events
            cell.bind(on_status_clicked=self.on_cell_clicked)
            cell.bind(on_status_double_clicked=self.on_cell_double_clicked)
            cell.bind(on_status_changed=self.on_cell_status_changed)
            
            self.cells_container.add_widget(cell)
            self.status_cells.append(cell)
            total_width += self.cell_size + 1  # +1 for spacing
            
        # Update container width
        self.cells_container.width = total_width
        self.width = self.name_width + total_width + 10  # +10 for spacing
        
    def on_cell_clicked(self, cell, habit_id: int, date_str: str, status: int):
        """Handle cell click event"""
        Logger.info(f'HabitRow: Cell clicked - habit {habit_id}, date {date_str}, status {status}')
        self.dispatch('on_status_clicked', habit_id, date_str, status)
        
    def on_cell_double_clicked(self, cell, habit_id: int, date_str: str, status: int):
        """Handle cell double-click event"""
        Logger.info(f'HabitRow: Cell double-clicked - habit {habit_id}, date {date_str}, status {status}')
        self.dispatch('on_status_double_clicked', habit_id, date_str, status)
        
    def on_cell_status_changed(self, cell, habit_id: int, date_str: str, old_status: int, new_status: int):
        """Handle cell status change event"""
        Logger.info(f'HabitRow: Status changed - habit {habit_id}, date {date_str}, {old_status} → {new_status}')
        
        # Update the dates_data to keep it in sync
        for date_info in self.dates_data:
            if date_info['date'] == date_str:
                date_info['status'] = new_status
                break
                
        self.dispatch('on_status_changed', habit_id, date_str, old_status, new_status)
        
    def update_cell_status(self, date_str: str, new_status: int):
        """
        Update the status of a specific cell.
        
        :param date_str: Date string in YYYY-MM-DD format
        :param new_status: New status value
        """
        for cell in self.status_cells:
            if cell.date_str == date_str:
                cell.update_status(new_status)
                break
                
        # Also update dates_data
        for date_info in self.dates_data:
            if date_info['date'] == date_str:
                date_info['status'] = new_status
                break
                
    def get_cell_status(self, date_str: str) -> int:
        """
        Get the status of a specific cell.
        
        :param date_str: Date string in YYYY-MM-DD format
        :return: Status value or 0 if not found
        """
        for cell in self.status_cells:
            if cell.date_str == date_str:
                return cell.status
        return 0
        
    def update_habit_data(self, habit_data: dict):
        """
        Update the row with new habit data.
        
        :param habit_data: Dictionary with habit information
        """
        self.habit_id = habit_data.get('id', 0)
        self.habit_name = habit_data.get('name', '')
        
        # Extract habit levels from parameters
        levels_param = habit_data.get('levels', '0')
        try:
            self.habit_levels = int(levels_param)
        except (ValueError, TypeError):
            self.habit_levels = 0
            
        # Update dates data
        self.dates_data = habit_data.get('dates', [])
        
    def highlight_today(self, today_date_str: str):
        """
        Highlight the cell for today's date.
        
        :param today_date_str: Today's date in YYYY-MM-DD format
        """
        for cell in self.status_cells:
            if cell.date_str == today_date_str:
                # Add some visual indication for today
                # This could be a different background color, border, etc.
                pass 