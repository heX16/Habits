"""
Table Widget - Compatibility Layer

This file provides backward compatibility for existing code.
It imports from the new separated architecture and re-exports the components.

New clean architecture:
- universal_table.py: TRULY universal table (just grid + text cells)
- habits_table.py: ALL habits-specific functionality (modes, statuses, double-clicks)
- table_widget.py: Compatibility layer (this file)
"""

# Import from universal table system (TRULY universal now)
from .universal_table import (
    UniversalCell as BaseUniversalCell,
    create_universal_table as create_base_universal_table,
    SimpleTable
)

# Import from habits-specific table system (ALL project logic)
from .habits_table import (
    HabitsCell,
    create_habits_table,
    create_habits_main_table,
    create_habits_calendar_table
)

# Default exports for backward compatibility
# Point to habits-specific implementations since this is a habits project
UniversalCell = HabitsCell
create_universal_table = create_habits_table

# Legacy compatibility functions
def create_cell(text="", style=None):
    """Legacy function - creates a simple label cell"""
    cell = HabitsCell(cell_mode='label', text=str(text))
    if style and isinstance(style, dict) and 'color' in style:
        cell.background_color = style['color']
    return cell


def create_table_widget(table_data):
    """Legacy function - creates a habits table"""
    return create_habits_table(table_data)


def create_calendar_table(table_data, habit_data=None, habits_model=None):
    """Legacy function - creates a habits calendar table"""
    if not table_data:
        return create_habits_table([[]])
        
    # Convert legacy format to new format
    converted_data = []
    for row_data in table_data:
        converted_row = []
        for cell_data in row_data:
            if isinstance(cell_data, dict) and 'day' in cell_data:
                # Calendar cell
                converted_cell = {
                    'cell_mode': 'calendar',
                    'day_num': cell_data.get('day', 0),
                    'value': cell_data.get('status', 0),
                    'date_str': cell_data.get('date', ''),
                    'habit_id': habit_data.get('id', 0) if habit_data else 0,
                    'habit_levels': int(habit_data.get('levels', 0)) if habit_data else 0,
                    'bad_habit': habit_data.get('bad_habit') == '1' if habit_data else False,
                    'habits_model': habits_model
                }
                converted_row.append(converted_cell)
            else:
                # Label cell
                converted_row.append(str(cell_data))
        converted_data.append(converted_row)
    
    return create_habits_table(converted_data)
