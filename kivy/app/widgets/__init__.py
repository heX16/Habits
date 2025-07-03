"""
Widgets package - Custom UI components

This package contains:
- StatusCell: Clickable habit status cell
- HabitRow: Complete habit row with cells
- DateHeader: Date column headers
- StatusIcon: Status display components
- FloatingMenu: Popup status menu
- NotificationBar: Message display
- Table widget utilities: create_table_widget, recreate_table, etc.
"""

# Widgets module for Habits Kivy app
from .status_cell import StatusCell
from .habit_row import HabitRow
from .date_header import DateHeader
from .status_menu_popup import StatusMenuPopup
from .table_widget import create_table_widget, recreate_table, update_table, update_cell, create_cell

__all__ = [
    'StatusCell', 'HabitRow', 'DateHeader', 'StatusMenuPopup',
    'create_table_widget', 'recreate_table', 'update_table', 'update_cell', 'create_cell'
] 