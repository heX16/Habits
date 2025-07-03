#!/usr/bin/env python3
"""
Simple ScrollView + GridLayout Table Test

Simple table based on ScrollView and GridLayout.
"""

from kivy.metrics import dp
from kivy.app import App  
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


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


def add_row(table_grid, table_data, row_data, table_style=None, row_style=None):
    """Adds a data row to the table using update_cell for abstraction"""
    # Create empty row first
    new_row = [""] * len(row_data)
    table_data.append(new_row)
    
    # Add empty style row if table_style exists
    if table_style is not None:
        new_style_row = [None] * len(row_data)
        if row_style:
            for i, style in enumerate(row_style):
                if i < len(new_style_row):
                    new_style_row[i] = style
        table_style.append(new_style_row)
    
    # Fill the row using update_cell
    row_idx = len(table_data) - 1
    for col_idx, value in enumerate(row_data):
        cell_style = None
        if table_style and row_idx < len(table_style) and col_idx < len(table_style[row_idx]):
            cell_style = table_style[row_idx][col_idx]
        update_cell(table_grid, table_data, row_idx, col_idx, value, cell_style)


def delete_row(table_grid, table_data, row_num, table_style=None):
    """Deletes a row from the table (both data and widgets)"""
      
    if row_num < 0 or row_num >= len(table_data):
        print(f"Error: Invalid row number {row_num}, table has {len(table_data)} rows")
        return False
    
    cols = table_grid.cols
    total_widgets = len(table_grid.children)
    
    # Check that we have enough widgets
    expected_widgets = len(table_data) * cols
    if total_widgets != expected_widgets:
        print(f"Warning: Expected {expected_widgets} widgets, but found {total_widgets}")
        return False
    
    # Remove row from data
    removed_row = table_data.pop(row_num)
    
    # Remove row from style if exists
    if table_style is not None and row_num < len(table_style):
        removed_style_row = table_style.pop(row_num)
    
    # Calculate widget indices for removal
    start_widget_idx = (len(table_data) - row_num) * cols - 1
    end_widget_idx = start_widget_idx - cols + 1
    
    # Remove widgets (remove from end so indices don't shift)
    widgets_to_remove = []
    for i in range(start_widget_idx, end_widget_idx - 1, -1):
        if 0 <= i < len(table_grid.children):
            widgets_to_remove.append(table_grid.children[i])
    
    for widget in widgets_to_remove:
        table_grid.remove_widget(widget)
    
    return True


def delete_col(table_grid, table_data, col_num, table_style=None):
    """Deletes a column from the table (both data and widgets)"""
        
    if col_num < 0 or col_num >= table_grid.cols:
        print(f"Error: Invalid col number {col_num}, table has {table_grid.cols} cols")
        return False
    
    if not table_data or len(table_data) == 0:
        print("Error: table_data is empty")
        return False
    
    # Check that all rows have enough columns
    for i, row in enumerate(table_data):
        if len(row) <= col_num:
            print(f"Error: Row {i} has only {len(row)} columns, cannot delete column {col_num}")
            return False
    
    cols = table_grid.cols
    rows = len(table_data)
    total_widgets = len(table_grid.children)
    
    # Check that we have enough widgets
    expected_widgets = rows * cols
    if total_widgets != expected_widgets:
        print(f"Warning: Expected {expected_widgets} widgets, but found {total_widgets}")
        return False
    
    # Collect widget indices for removal
    widgets_to_remove = []
    
    for row in range(rows):
        # Calculate widget index
        widget_idx = total_widgets - 1 - (row * cols + col_num)
        
        if 0 <= widget_idx < len(table_grid.children):
            widgets_to_remove.append(table_grid.children[widget_idx])
    
    # Remove widgets
    for widget in widgets_to_remove:
        table_grid.remove_widget(widget)
    
    # Remove column from data (from all rows)
    for row in table_data:
        if col_num < len(row):
            removed_cell = row.pop(col_num)
    
    # Remove column from style (from all rows)
    if table_style is not None:
        for row in table_style:
            if col_num < len(row):
                removed_style = row.pop(col_num)
    
    # Decrease the number of columns in GridLayout
    table_grid.cols -= 1
    
    return True


def insert_row(table_grid, table_data, row_num, row_data, table_style=None, row_style=None):
    """Inserts a row at an arbitrary position in the table"""
    
    if row_num < 0 or row_num > len(table_data):
        print(f"Error: Invalid row number {row_num}, table has {len(table_data)} rows")
        return False
    
    if not row_data:
        print("Error: row_data is empty")
        return False
    
    cols = table_grid.cols
    
    # Check that row_data has the correct number of columns
    if len(row_data) != cols:
        print(f"Error: row_data has {len(row_data)} columns, but table has {cols} columns")
        return False
    
    # Insert data into table_data
    table_data.insert(row_num, list(row_data))
    
    # Insert style row if table_style exists
    if table_style is not None:
        new_style_row = [None] * len(row_data)
        if row_style:
            for i, style in enumerate(row_style):
                if i < len(new_style_row):
                    new_style_row[i] = style
        table_style.insert(row_num, new_style_row)
    
    total_rows = len(table_data)
    
    print(f"Inserting row at position {row_num}")
    print(f"Children before: {len(table_grid.children)}")
    
    # LOOP 1: Calculate all indices for inserting new row widgets
    insert_indices = []
    
    # For row row_num in the new structure, position in children (reverse order):
    base_position = (total_rows - row_num - 1) * cols
    
    # Insert widgets left to right (from first column to last)
    for col in range(cols):
        # Widget position = row base position + column offset
        insert_index = base_position + col
        
        insert_indices.append((col, insert_index))
        print(f"Col {col}: will insert at index {insert_index}")
    
    # LOOP 2: Create and insert widgets at calculated indices with actual text and style
    for col, insert_index in insert_indices:
        # Take data in reverse order because children are stored in reverse order
        cell_data = row_data[cols - 1 - col]
        
        # Get style for this cell
        cell_style = None
        if table_style and row_num < len(table_style):
            style_col = cols - 1 - col  # Same reverse order as data
            if style_col < len(table_style[row_num]):
                cell_style = table_style[row_num][style_col]
        
        # Create widget using create_cell function with actual text and style
        label = create_cell(cell_data, cell_style)
        
        # Insert widget at pre-calculated index
        table_grid.add_widget(label, index=insert_index)
        print(f"Inserted widget for col {col} at index {insert_index}")
    
    print(f"Children after: {len(table_grid.children)}")
    print(f"Table now has {len(table_data)} rows")
    
    return True


def insert_col(table_grid, table_data, col_num, col_data, table_style=None, col_style=None):
    """Inserts a column at an arbitrary position in the table"""
    
    if col_num < 0 or col_num > table_grid.cols:
        print(f"Error: Invalid col number {col_num}, table has {table_grid.cols} cols")
        return False
    
    if not col_data:
        print("Error: col_data is empty")
        return False
    
    if len(col_data) != len(table_data):
        print(f"Error: col_data has {len(col_data)} rows, but table has {len(table_data)} rows")
        return False
    
    # Insert column data into all rows of table_data
    for i, row in enumerate(table_data):
        if i < len(col_data):
            row.insert(col_num, str(col_data[i]))
    
    # Insert column style into all rows of table_style
    if table_style is not None:
        for i, row in enumerate(table_style):
            style_value = None
            if col_style and i < len(col_style):
                style_value = col_style[i]
            row.insert(col_num, style_value)
    
    old_cols = table_grid.cols
    rows = len(table_data)
    
    # Increase the number of columns in GridLayout
    table_grid.cols += 1
    new_cols = table_grid.cols
    
    print(f"Inserting column at position {col_num}")
    print(f"Columns: {old_cols} -> {new_cols}")
    print(f"Children before: {len(table_grid.children)}")
    
    # LOOP 1: Calculate all indices for insertion
    insert_indices = []
    
    # Go from bottom to top so indices don't shift during insertion
    for row in range(rows - 1, -1, -1):
        # For row row we need to insert a widget in column col_num
        
        # Number of widgets we've already inserted (in rows below)
        widgets_already_inserted = (rows - 1 - row)
        
        # Current number of children (including already inserted)
        current_children_count = old_cols * rows + widgets_already_inserted
        
        # Number of widgets "to the left and above" in the old structure
        widgets_before_in_old_structure = row * old_cols + col_num
        
        # Index for insertion (children in reverse order)
        insert_index = current_children_count - widgets_before_in_old_structure
        
        insert_indices.append((row, insert_index))
        print(f"Row {row}: will insert at index {insert_index}")
    
    # LOOP 2: Create and insert widgets at calculated indices with actual text and style
    for row, insert_index in insert_indices:
        cell_data = col_data[row] if row < len(col_data) else ""
        
        # Get style for this cell
        cell_style = None
        if table_style and row < len(table_style) and col_num < len(table_style[row]):
            cell_style = table_style[row][col_num]
        
        # Create widget using create_cell function with actual text and style
        label = create_cell(cell_data, cell_style)
        
        # Insert widget at pre-calculated index
        table_grid.add_widget(label, index=insert_index)
        print(f"Inserted widget for row {row} at index {insert_index}")
    
    print(f"Children after: {len(table_grid.children)}")
    
    return True



class SimpleTableApp(App):
    """Simple application with table"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table_data = []
        self.table_style = []
        self.table_grid = None
        self.scroll_widget = None
        
    def build(self):
        # Main vertical layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # First row of buttons
        buttons_layout1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Create first 5 buttons
        button1 = Button(text="Add Row", size_hint_x=0.2, on_press=self.on_add_row)
        button2 = Button(text="Insert Row", size_hint_x=0.2, on_press=self.on_insert_row)
        button3 = Button(text="Update Cell", size_hint_x=0.2, on_press=self.on_update_cell)
        button4 = Button(text="Update Table", size_hint_x=0.2, on_press=self.on_update_table)
        button5 = Button(text="Change Data", size_hint_x=0.2, on_press=self.on_change_data)
        
        # Add first buttons to first layout
        buttons_layout1.add_widget(button1)
        buttons_layout1.add_widget(button2)
        buttons_layout1.add_widget(button3)
        buttons_layout1.add_widget(button4)
        buttons_layout1.add_widget(button5)
        
        # Second row of buttons for changing table size
        buttons_layout2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Create buttons for size changes
        button6 = Button(text="Insert Col", size_hint_x=0.25, on_press=self.on_insert_col)
        button7 = Button(text="Delete Col", size_hint_x=0.25, on_press=self.on_delete_col_new)
        button8 = Button(text="+1 rows", size_hint_x=0.25, on_press=self.on_add_row_size)
        button9 = Button(text="Count Widgets", size_hint_x=0.25, on_press=self.on_count_widgets)
        
        # Add second buttons to second layout
        buttons_layout2.add_widget(button6)
        buttons_layout2.add_widget(button7)
        buttons_layout2.add_widget(button8)
        buttons_layout2.add_widget(button9)
        
        # Initialize table data (first row - headers)
        self.table_data = [
            ["Col1", "Col2", "Col3", "Col4", "Col5", "Col6", "Col7"]  # Headers
        ]
        
        # Initialize table style (corresponding to table_data)
        self.table_style = [
            [None, None, None, None, None, None, None]  # Headers with no style
        ]
        
        # Add data rows directly to table_data during initialization (before widgets are created)
        for col in range(1, 11):  # 10 rows
            self.table_data.append([f"1x{col}", f"2x{col}", f"3x{col}", f"4x{col}", f"5x{col}", f"6x{col}", f"7x{col}"])
            self.table_style.append([None, None, None, None, None, None, None])  # No style for data rows
        
        # Create table widget
        self.scroll_widget, self.table_grid = create_table_widget(self.table_data)
        
        # Fill the table
        recreate_table(self.table_grid, self.table_data, self.table_style)
        
        # Add elements to main layout
        main_layout.add_widget(buttons_layout1)
        main_layout.add_widget(buttons_layout2)
        main_layout.add_widget(self.scroll_widget)
        
        return main_layout
    

    
    def on_add_row(self, instance):
        """Adds a new row to the table"""
        row_num = len(self.table_data)  # -1 for headers + 1 for new number = len
        new_row = [f"1x{row_num}", f"2x{row_num}", f"3x{row_num}", f"4x{row_num}", f"5x{row_num}", f"6x{row_num}", f"7x{row_num}"]
        add_row(self.table_grid, self.table_data, new_row, self.table_style)
        recreate_table(self.table_grid, self.table_data, self.table_style)
        print(f"Added row. Total rows: {len(self.table_data) - 1}")  # -1 for headers
    
    def on_delete_row(self, instance):
        """Deletes the last row from the table"""
        if len(self.table_data) > 1:  # Keep headers
            self.table_data.pop()
            if self.table_style and len(self.table_style) > 1:
                self.table_style.pop()
            recreate_table(self.table_grid, self.table_data, self.table_style)
            print(f"Removed row. Total rows: {len(self.table_data) - 1}")  # -1 for headers
    
    def on_delete_row_new(self, instance):
        """Deletes the second row from the table (first data row) using new delete_row function"""
        if len(self.table_data) > 1:  # Check that there's data besides headers
            # Delete first data row (index 1, since 0 is headers)
            success = delete_row(self.table_grid, self.table_data, 1, self.table_style)
            if success:
                print(f"Successfully deleted row. Total rows: {len(self.table_data) - 1}")  # -1 for headers
            else:
                print("Failed to delete row")
        else:
            print("No data rows to delete (only headers remain)")
    
    def on_update_cell(self, instance):
        """Demonstration of cell update"""
        if len(self.table_data) > 1:  # Check that there's data besides headers
            # Update first cell of first data row (not headers)
            update_cell(self.table_grid, self.table_data, 1, 0, "UPDATED!")
            print("Updated cell (1,0)")
    
    def on_update_table(self, instance):
        """Updates table without recreating widgets"""
        if self.table_grid and self.table_data:
            success = update_table(self.table_grid, self.table_data, self.table_style)
            if success:
                print("Table updated successfully")
            else:
                print("Failed to update table")
        else:
            print("Table not initialized")
    
    def on_refresh_table(self, instance):
        """Force refreshes the table"""
        recreate_table(self.table_grid, self.table_data, self.table_style)
        print("Table refreshed")
    
    def on_change_data(self, instance):
        """Changes some data in the table for testing update_table with colored cells"""
        if self.table_data and len(self.table_data) > 1:
            import random
            
            # Change random cells using update_cell for abstraction
            rows_to_change = min(3, len(self.table_data) - 1)  # Don't touch headers
            for i in range(rows_to_change):
                row_idx = random.randint(1, len(self.table_data) - 1)  # Don't touch headers
                col_idx = random.randint(0, len(self.table_data[row_idx]) - 1)
                old_value = self.table_data[row_idx][col_idx]
                new_value = f"NEW_{random.randint(1, 999)}"
                
                # Add some color to demonstrate styling
                cell_style = None
                if i == 0:  # First changed cell gets red color
                    cell_style = {'color': [1, 0, 0, 1]}  # Red
                elif i == 1:  # Second changed cell gets green color
                    cell_style = {'color': [0, 1, 0, 1]}  # Green
                elif i == 2:  # Third changed cell gets blue color
                    cell_style = {'color': [0, 0, 1, 1]}  # Blue
                
                # Update the style in table_style (expand if needed)
                if self.table_style:
                    # Ensure table_style has enough rows
                    while len(self.table_style) <= row_idx:
                        self.table_style.append([])
                    
                    # Ensure the row has enough columns
                    while len(self.table_style[row_idx]) <= col_idx:
                        self.table_style[row_idx].append(None)
                    
                    # Now safely assign the style (Python allows mixed types in lists)
                    self.table_style[row_idx][col_idx] = cell_style  
                
                update_cell(self.table_grid, self.table_data, row_idx, col_idx, new_value, cell_style)
                print(f"Changed cell ({row_idx},{col_idx}): '{old_value}' -> '{new_value}' with style {cell_style}")
            
            print("Data changed. Use 'Update Table' to apply changes efficiently.")
        else:
            print("No data to change")
    
    def on_count_widgets(self, instance):
        """Prints the number of widgets in the table"""
        if self.table_grid:
            count = len(self.table_grid.children)
            print(f"Number of widgets in table: {count}")
            print(f"Table size: {self.table_grid.cols} columns")
            print(f"Total data rows: {len(self.table_data)}")
        else:
            print("Table not created")
    
    def on_add_col(self, instance):
        """Increases the number of columns by 1"""
        if self.table_grid:
            old_cols = self.table_grid.cols
            self.table_grid.cols += 1
            print(f"Columns: {old_cols} -> {self.table_grid.cols}")
            print(f"Widgets in table: {len(self.table_grid.children)}")
    
    def on_remove_col(self, instance):
        """Decreases the number of columns by 1"""
        if self.table_grid and self.table_grid.cols > 1:
            old_cols = self.table_grid.cols
            self.table_grid.cols -= 1
            print(f"Columns: {old_cols} -> {self.table_grid.cols}")
            print(f"Widgets in table: {len(self.table_grid.children)}")
        else:
            print("Cannot decrease columns below 1")
    
    def on_add_row_size(self, instance):
        """Increases the number of rows by 1"""
        if self.table_grid:
            old_rows = self.table_grid.rows if self.table_grid.rows else "auto"
            if not self.table_grid.rows:
                self.table_grid.rows = 2  # Set minimum 2 rows
            else:
                self.table_grid.rows += 1
            print(f"Rows: {old_rows} -> {self.table_grid.rows}")
            print(f"Widgets in table: {len(self.table_grid.children)}")
    
    def on_remove_row_size(self, instance):
        """Decreases the number of rows by 1"""
        if self.table_grid and self.table_grid.rows and self.table_grid.rows > 1:
            old_rows = self.table_grid.rows
            self.table_grid.rows -= 1
            print(f"Rows: {old_rows} -> {self.table_grid.rows}")
            print(f"Widgets in table: {len(self.table_grid.children)}")
        else:
            print("Cannot decrease rows below 1 or rows are in auto mode")
    
    def on_delete_col_new(self, instance):
        """Deletes the first column from the table using new delete_col function"""
        if self.table_grid and self.table_grid.cols > 1:
            # Delete first column (index 0)
            success = delete_col(self.table_grid, self.table_data, 0, self.table_style)
            if success:
                print(f"Successfully deleted column. Remaining cols: {self.table_grid.cols}")
                print(f"Remaining widgets: {len(self.table_grid.children)}")
            else:
                print("Failed to delete column")
        else:
            print("Cannot delete column - only 1 column remaining")
    
    def on_insert_row(self, instance):
        """Inserts a new row at position 2 (after headers and first data row)"""
        if self.table_grid and len(self.table_data) > 0:
            # Create data for new row
            new_row_data = ["NEW", "ROW", "INSERT", "TEST", "HERE", "NOW", "!!!"]
            
            # Insert at position 2 (after headers and first data row)
            insert_position = 2 if len(self.table_data) > 1 else 1
            
            success = insert_row(self.table_grid, self.table_data, insert_position, new_row_data, self.table_style)
            if success:
                print(f"Successfully inserted row at position {insert_position}")
                print(f"Table now has {len(self.table_data)} rows total")
                print(f"Widgets in table: {len(self.table_grid.children)}")
            else:
                print("Failed to insert row")
        else:
            print("Cannot insert row - table not initialized")
    
    def on_insert_col(self, instance):
        """Inserts a new column at position 2 (between Col2 and Col3)"""
        if self.table_grid and len(self.table_data) > 0:
            # Create data for new column (one value for each row)
            col_data = ["NEW_COL"]  # Header for new column
            
            # Add data for each data row
            for i in range(1, len(self.table_data)):  # Start from 1 since 0 is headers
                col_data.append(f"N{i}")
            
            # Insert at position 2 (between Col2 and Col3)
            insert_position = 2
            
            success = insert_col(self.table_grid, self.table_data, insert_position, col_data, self.table_style)
            if success:
                print(f"Successfully inserted column at position {insert_position}")
                print(f"Table now has {self.table_grid.cols} columns")
                print(f"Widgets in table: {len(self.table_grid.children)}")
            else:
                print("Failed to insert column")
        else:
            print("Cannot insert column - table not initialized")


if __name__ == '__main__':
    SimpleTableApp().run()
