"""
Date Header Widget

Widget for displaying date headers in the habits table.
Shows day names, dates, and highlights today.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from datetime import date


class DateHeader(BoxLayout):
    """
    Header widget for displaying date information.
    """
    
    # Properties for data binding
    date_str = StringProperty('')
    day_name = StringProperty('')
    day_number = NumericProperty(0)
    month_name = StringProperty('')
    is_today = BooleanProperty(False)
    is_weekend = BooleanProperty(False)
    
    # Visual properties
    header_width = NumericProperty(50)
    header_height = NumericProperty(60)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set up the layout
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (self.header_width, self.header_height)
        self.spacing = 2
        
        # Create labels
        self.day_label = Label(
            text=self.day_name,
            size_hint=(1, 0.4),
            font_size=12,
            bold=True,
            halign='center',
            valign='middle'
        )
        
        self.date_label = Label(
            text=str(self.day_number),
            size_hint=(1, 0.4),
            font_size=14,
            bold=True,
            halign='center',
            valign='middle'
        )
        
        self.month_label = Label(
            text=self.month_name,
            size_hint=(1, 0.2),
            font_size=10,
            halign='center',
            valign='middle'
        )
        
        # Add labels to layout
        self.add_widget(self.day_label)
        self.add_widget(self.date_label)
        self.add_widget(self.month_label)
        
        # Bind property changes
        self.bind(day_name=self.update_day_label)
        self.bind(day_number=self.update_date_label)
        self.bind(month_name=self.update_month_label)
        self.bind(is_today=self.update_styling)
        self.bind(is_weekend=self.update_styling)
        
        # Initial styling update
        self.update_styling()
        
    def update_day_label(self, *args):
        """Update the day name label"""
        self.day_label.text = self.day_name
        
    def update_date_label(self, *args):
        """Update the date number label"""
        self.date_label.text = str(self.day_number)
        
    def update_month_label(self, *args):
        """Update the month name label"""
        self.month_label.text = self.month_name
        
    def update_styling(self, *args):
        """Update styling based on properties"""
        # Update colors based on state
        if self.is_today:
            # Highlight today with blue color
            text_color = (0, 0.5, 1, 1)  # Blue
            bg_color = (0.9, 0.95, 1, 1)  # Light blue background
        elif self.is_weekend:
            # Weekend styling
            text_color = (0.7, 0.4, 0.4, 1)  # Reddish
            bg_color = (1, 0.95, 0.95, 1)   # Light red background
        else:
            # Regular weekday styling
            text_color = (0.2, 0.2, 0.2, 1)  # Dark gray
            bg_color = (0.95, 0.95, 0.95, 1)  # Light gray background
            
        # Apply colors to labels
        self.day_label.color = text_color
        self.date_label.color = text_color
        self.month_label.color = text_color
        
        # Apply background color (would need canvas implementation)
        if hasattr(self, 'background_color'):
            self.background_color = bg_color
            
    def set_date_info(self, date_info: dict):
        """
        Set date information from a dictionary.
        
        :param date_info: Dictionary with date information
        """
        self.date_str = date_info.get('date', '')
        self.day_name = date_info.get('day_name', '')
        self.day_number = date_info.get('day_number', 0)
        self.month_name = date_info.get('month_name', '')
        self.is_today = date_info.get('is_today', False)
        self.is_weekend = date_info.get('is_weekend', False)
        
    @staticmethod
    def create_from_date_info(date_info: dict, width: int = 50, height: int = 60) -> 'DateHeader':
        """
        Create a DateHeader widget from date information.
        
        :param date_info: Dictionary with date information
        :param width: Header width
        :param height: Header height
        :return: DateHeader widget
        """
        header = DateHeader(
            header_width=width,
            header_height=height
        )
        header.set_date_info(date_info)
        return header 