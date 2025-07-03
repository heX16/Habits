#!/usr/bin/env python3
"""
Habits Simple Tracker - Kivy Version

Main application entry point for the Kivy-based habits tracking app.
Cross-platform habits tracker with 7-day table view.
Updated to use KivyMD components including MDDataTable.
"""

import os
import sys
import kivy
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger
from kivy.resources import resource_add_path
from kivy.lang import Builder

# KivyMD imports
from kivymd.app import MDApp
from kivymd.theming import ThemeManager

# Add the project root to the path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.screens import MainTrackerScreen, OptionsScreen
from app.services.app_state_manager import AppStateManager


def create_cell(text="", style=None):
    """Creates a standardized cell widget (Label) with given text and style"""
    label = Label(
        text=str(text),
        size_hint_y=None,
        height=dp(40),
        halign="center",
        valign="middle"
    )
    label.bind(size=label.setter('text_size'))  # type: ignore
    
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
    table_grid.bind(minimum_height=table_grid.setter('height'))  # type: ignore
    
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





class HabitsApp(MDApp):
    """Main KivyMD application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger.info('HabitsApp: Initializing KivyMD application')
        
        # App state manager
        self.state_manager = None
        
        # Screen manager
        self.screen_manager = None
        
        # Main screen
        self.main_screen = None
        
        # Options screen
        self.options_screen = None
        
        # Set theme
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Orange"
        
    def build(self):
        """Build the application UI"""
        Logger.info('HabitsApp: Building application')
        
        try:
            # Initialize app state manager
            self.state_manager = AppStateManager()
            
            # Load the main screen layout
            kv_file = os.path.join(os.path.dirname(__file__), 'app', 'assets', 'kv', 'main_tracker.kv')
            if os.path.exists(kv_file):
                Builder.load_file(kv_file)
                Logger.info(f'HabitsApp: Loaded KV file: {kv_file}')
            else:
                Logger.warning(f'HabitsApp: KV file not found: {kv_file}')
            
            # Create screen manager
            self.screen_manager = ScreenManager()
            
            # Create main screen
            self.main_screen = MainTrackerScreen(name='main_tracker')
            
            # Create options screen
            self.options_screen = OptionsScreen(name='options')
            
            # Connect screens to shared habits model
            if self.state_manager.is_database_ready():
                shared_model = self.state_manager.get_habits_model()
                self.main_screen.habits_model = shared_model
                self.options_screen.habits_model = shared_model
                Logger.info('HabitsApp: Connected screens to shared habits model')
            
            # Add screens to screen manager
            self.screen_manager.add_widget(self.main_screen)
            self.screen_manager.add_widget(self.options_screen)
            
            # Set initial screen
            self.screen_manager.current = 'main_tracker'
            
            # Set window title
            self.title = 'Habits Simple Tracker'
            
            Logger.info('HabitsApp: Application built successfully')
            return self.screen_manager
            
        except Exception as e:
            Logger.error(f'HabitsApp: Error building application: {e}')
            raise
            
    def on_start(self):
        """Called when the app starts"""
        Logger.info('HabitsApp: Application started')
        
        # Print database info
        if self.state_manager:
            db_info = self.state_manager.get_database_info()
            Logger.info(f'HabitsApp: Database info: {db_info}')
            
            # Add sample data if database is empty
            if db_info.get('habits_count', 0) == 0:
                Logger.info('HabitsApp: Database is empty, adding sample data')
                try:
                    self.state_manager.add_sample_data()
                    
                    # Refresh the main screen
                    if self.main_screen:
                        self.main_screen.load_current_week()
                        
                except Exception as e:
                    Logger.error(f'HabitsApp: Error adding sample data: {e}')
        
    def on_pause(self):
        """Called when the app is paused (Android)"""
        Logger.info('HabitsApp: Application paused')
        if self.state_manager:
            self.state_manager.on_app_pause()
        return True  # Return True to pause
        
    def on_resume(self):
        """Called when the app is resumed (Android)"""
        Logger.info('HabitsApp: Application resumed')
        if self.state_manager:
            self.state_manager.on_app_resume()
            
    def on_stop(self):
        """Called when the app is stopped"""
        Logger.info('HabitsApp: Application stopping')
        if self.state_manager:
            self.state_manager.on_app_stop()
            
    def get_application_config(self):
        """Get path to the application config file"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        Logger.info(f'HabitsApp: Using config file: {config_path}')
        return config_path


def main():
    """Main entry point"""
    Logger.info('Starting Habits Simple Tracker (Kivy Version)')
    
    try:
        # Create and run the app
        app = HabitsApp()
        app.run()
        
    except Exception as e:
        Logger.error(f'Failed to start application: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
        

if __name__ == '__main__':
    main() 