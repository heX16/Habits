"""
Widgets package - Custom UI components

This package contains:
- UniversalCell: Universal cell that can work as label, interactive status cell, or calendar cell
- HabitRow: Complete habit row with cells
- DateHeader: Date column headers
- StatusMenuPopup: Popup status menu
- NotificationManager: Simple notification system (web version port)
- Table widget utilities: create_universal_table, create_table_widget (legacy), etc.
"""

# Widgets module for Habits Kivy app
from .habit_row import HabitRow
from .date_header import DateHeader
from .status_menu_popup import StatusMenuPopup
from .notification_manager import NotificationManager, get_notification_manager
from .table_widget import (
    UniversalCell, 
    create_universal_table, 
    create_table_widget, 
    create_calendar_table, 
    create_cell
)

__all__ = [
    'UniversalCell', 'HabitRow', 'DateHeader', 'StatusMenuPopup',
    'NotificationManager', 'get_notification_manager',
    'create_universal_table', 'create_table_widget', 'create_calendar_table', 'create_cell'
] 