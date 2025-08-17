"""
Status Menu Popup Widget

Popup menu for selecting habit status on double click.
Displays available statuses based on habit settings.
"""

from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.logger import Logger

class StatusMenuPopup(Popup):
    """Popup menu for habit status selection"""
    
    def __init__(self, habit_data, current_status, on_status_selected, **kwargs):
        """
        Initialize status menu
        
        Args:
            habit_data: habit data with parameters
            current_status: current cell status
            on_status_selected: callback function for status selection
        """
        super().__init__(**kwargs)
        
        self.habit_data = habit_data
        self.current_status = current_status
        self.on_status_selected = on_status_selected
        
        # Popup settings
        self.title = f"Status: {habit_data.get('name', 'Habit')}"
        self.size_hint = (0.8, 0.6)
        self.auto_dismiss = True
        
        # Create content
        self.content = self._create_content()
        
        Logger.info(f"StatusMenuPopup: Created for habit '{habit_data.get('name')}', current status: {current_status}")
    
    def _create_content(self):
        """Create popup content with status buttons"""
        layout = GridLayout(cols=1, spacing=dp(10), padding=dp(10))
        
        # Header
        header_label = Label(
            text="Select status:",
            size_hint_y=None,
            height=dp(30),
            font_size='16sp'
        )
        layout.add_widget(header_label)
        
        # Get available statuses
        available_statuses = self._get_available_statuses()
        
        # Create status buttons grid
        buttons_grid = GridLayout(cols=2, spacing=dp(5))
        
        for status_value, status_info in available_statuses.items():
            button = Button(
                text=status_info['text'],
                size_hint_y=None,
                height=dp(50),
                font_size='14sp'
            )
            
            # Highlight current status
            if status_value == self.current_status:
                button.background_color = (0.3, 0.6, 1, 1)  # Blue color
            else:
                button.background_color = (0.9, 0.9, 0.9, 1)  # Gray color
            
            button.bind(on_press=lambda btn, status=status_value: self._on_status_button_press(status))
            buttons_grid.add_widget(button)
        
        layout.add_widget(buttons_grid)
        
        # Cancel button
        cancel_button = Button(
            text="Cancel",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.8, 0.3, 0.3, 1)
        )
        cancel_button.bind(on_press=self._on_cancel)
        layout.add_widget(cancel_button)
        
        return layout
    
    def _get_available_statuses(self):
        """
        Determine available statuses based on habit settings
        
        Returns:
            dict: dictionary {status_value: {'text': 'display_text', 'icon': 'icon_name'}}
        """
        # Get habit mode (default level3)
        mode = self.habit_data.get('mode', 'level3')
        levels = self.habit_data.get('levels', 3)
        
        statuses = {}
        
        if mode == 'level1' or levels == 1:
            # Basic statuses only
            statuses = {
                0: {'text': '❌ Not done', 'icon': 'not_set'},
                2: {'text': '✅ Done', 'icon': 'done'},
                9: {'text': '❌ Failed', 'icon': 'fail'}
            }
        elif mode == 'level10' or levels == 10:
            # Numeric statuses 0-9
            statuses = {
                0: {'text': '0️⃣ Not done', 'icon': 'not_set'},
                10: {'text': '0️⃣ Zero', 'icon': 'number_0'},
                11: {'text': '1️⃣ One', 'icon': 'number_1'},
                12: {'text': '2️⃣ Two', 'icon': 'number_2'},
                13: {'text': '3️⃣ Three', 'icon': 'number_3'},
                14: {'text': '4️⃣ Four', 'icon': 'number_4'},
                15: {'text': '5️⃣ Five', 'icon': 'number_5'},
                16: {'text': '6️⃣ Six', 'icon': 'number_6'},
                17: {'text': '7️⃣ Seven', 'icon': 'number_7'},
                18: {'text': '8️⃣ Eight', 'icon': 'number_8'},
                19: {'text': '9️⃣ Nine', 'icon': 'number_9'},
                9: {'text': '❌ Failed', 'icon': 'fail'}
            }
        else:
            # Full level3 mode (default)
            statuses = {
                0: {'text': '❌ Not done', 'icon': 'not_set'},
                1: {'text': '🟡 Mini', 'icon': 'done_mini'},
                2: {'text': '✅ Done', 'icon': 'done'},
                3: {'text': '⭐ Elite', 'icon': 'done_elite'},
                9: {'text': '❌ Failed', 'icon': 'fail'}
            }
        
        Logger.info(f"StatusMenuPopup: Available statuses for mode '{mode}': {list(statuses.keys())}")
        return statuses
    
    def _on_status_button_press(self, status_value):
        """Handle status button press"""
        Logger.info(f"StatusMenuPopup: Status selected: {status_value}")
        
        if self.on_status_selected:
            self.on_status_selected(status_value)
        
        self.dismiss()
    
    def _on_cancel(self, button):
        """Handle selection cancellation"""
        Logger.info("StatusMenuPopup: Cancelled")
        self.dismiss()
    
    @staticmethod
    def show_for_cell(habit_data, current_status, on_status_selected):
        """
        Static method to show popup
        
        Args:
            habit_data: habit data
            current_status: current status
            on_status_selected: callback function
        """
        popup = StatusMenuPopup(
            habit_data=habit_data,
            current_status=current_status,
            on_status_selected=on_status_selected
        )
        popup.open()
        return popup 