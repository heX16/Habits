#!/usr/bin/env python3
"""
Test script for table styling system
"""

from simple_table import create_cell, update_cell, create_table_widget, recreate_table
from kivy.app import App  
from kivy.uix.boxlayout import BoxLayout  
from kivy.uix.button import Button  


class StyleTestApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        # Test data with different styles
        self.table_data = [
            ["Name", "Age", "Status"],
            ["Alice", "25", "Active"],
            ["Bob", "30", "Inactive"],
            ["Charlie", "22", "Active"]
        ]
        
        # Test styles with colors
        self.table_style = [
            [None, None, None],  # Headers - no style
            [{'color': [1, 0, 0, 1]}, None, {'color': [0, 1, 0, 1]}],  # Red name, green status
            [{'color': [0, 0, 1, 1]}, None, {'color': [1, 0, 0, 1]}],  # Blue name, red status
            [None, {'color': [1, 1, 0, 1]}, {'color': [0, 1, 0, 1]}]   # Yellow age, green status
        ]
        
        # Create table
        self.scroll_widget, self.table_grid = create_table_widget(self.table_data)
        recreate_table(self.table_grid, self.table_data, self.table_style)
        
        # Test button
        button = Button(
            text="Test Update Cell with Style",
            size_hint_y=None,
            height=50,
            on_press=self.test_update
        )
        
        layout.add_widget(button)
        layout.add_widget(self.scroll_widget)
        
        return layout
    
    def test_update(self, instance):
        """Test updating a cell with new style"""
        # Update cell (1,1) with purple color
        purple_style = {'color': [1, 0, 1, 1]}  # Purple
        update_cell(self.table_grid, self.table_data, 1, 1, "26", purple_style)
        
        # Update style in our table_style
        self.table_style[1][1] = purple_style
        
        print("Updated cell (1,1) with purple color")


if __name__ == '__main__':
    StyleTestApp().run() 