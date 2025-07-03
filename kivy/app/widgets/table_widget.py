"""
Table Widget Utilities

Provides functions for creating and managing table widgets with ScrollView and GridLayout.
Extracted from main.py for clean imports and better code organization.
"""

from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp


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
