"""
Notification Popup Widget

Provides a unified notification system for the Kivy application.
Displays success, error, warning, and info messages with proper styling.
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty


class NotificationPopup(Popup):
    """
    Popup for displaying notifications with different types.
    
    Supports types: success, error, warning, info
    Auto-dismisses after a timeout or can be manually closed.
    """
    
    notification_type = StringProperty('info')
    auto_dismiss_timeout = NumericProperty(5.0)  # seconds
    
    def __init__(self, message: str, notification_type: str = 'info', 
                 title: str = None, timeout: float = 5.0, **kwargs):
        """
        Initialize notification popup.
        
        :param message: The message to display
        :param notification_type: Type of notification ('success', 'error', 'warning', 'info')
        :param title: Optional title (auto-generated if None)
        :param timeout: Auto-dismiss timeout in seconds (0 to disable)
        """
        self.notification_type = notification_type
        self.auto_dismiss_timeout = timeout
        
        # Auto-generate title if not provided
        if title is None:
            title = self._get_default_title(notification_type)
        
        # Set popup properties
        super().__init__(
            title=title,
            size_hint=(None, None),
            size=(dp(350), dp(200)),
            auto_dismiss=False,  # We handle dismissal ourselves
            **kwargs
        )
        
        # Build content
        self._build_content(message)
        
        # Set colors based on type
        self._apply_styling()
        
        # Schedule auto-dismiss if timeout > 0
        if self.auto_dismiss_timeout > 0:
            Clock.schedule_once(self._auto_dismiss, self.auto_dismiss_timeout)
        
        Logger.info(f'NotificationPopup: Created {notification_type} notification: {message}')
    
    def _get_default_title(self, notification_type: str) -> str:
        """Get default title based on notification type."""
        titles = {
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information'
        }
        return titles.get(notification_type, 'Notification')
    
    def _build_content(self, message: str):
        """Build the popup content layout."""
        # Main layout
        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20)
        )
        
        # Message label
        message_label = Label(
            text=message,
            text_size=(dp(310), None),  # Enable text wrapping
            halign='center',
            valign='middle',
            markup=True
        )
        
        # Close button
        close_button = Button(
            text='Close',
            size_hint=(None, None),
            size=(dp(100), dp(40)),
            pos_hint={'center_x': 0.5}
        )
        close_button.bind(on_press=self._on_close)
        
        # Add widgets to layout
        layout.add_widget(message_label)
        layout.add_widget(close_button)
        
        self.content = layout
    
    def _apply_styling(self):
        """Apply styling based on notification type."""
        # Color schemes for different notification types
        color_schemes = {
            'success': {
                'title_color': (0.2, 0.8, 0.2, 1),  # Green
                'separator_color': (0.2, 0.6, 0.2, 1)
            },
            'error': {
                'title_color': (0.8, 0.2, 0.2, 1),  # Red
                'separator_color': (0.6, 0.2, 0.2, 1)
            },
            'warning': {
                'title_color': (0.8, 0.6, 0.2, 1),  # Orange
                'separator_color': (0.6, 0.4, 0.2, 1)
            },
            'info': {
                'title_color': (0.2, 0.4, 0.8, 1),  # Blue
                'separator_color': (0.2, 0.3, 0.6, 1)
            }
        }
        
        scheme = color_schemes.get(self.notification_type, color_schemes['info'])
        
        # Apply colors
        self.title_color = scheme['title_color']
        self.separator_color = scheme['separator_color']
    
    def _on_close(self, button):
        """Handle close button press."""
        self.dismiss()
    
    def _auto_dismiss(self, dt):
        """Auto-dismiss the notification after timeout."""
        self.dismiss()
    
    def dismiss(self):
        """Override dismiss to add logging."""
        Logger.info(f'NotificationPopup: Dismissing {self.notification_type} notification')
        super().dismiss()


class NotificationToast(BoxLayout):
    """
    Toast-style notification that appears at the top of the screen.
    Non-intrusive alternative to popup notifications.
    """
    
    def __init__(self, message: str, notification_type: str = 'info', 
                 timeout: float = 3.0, **kwargs):
        """
        Initialize toast notification.
        
        :param message: The message to display
        :param notification_type: Type of notification ('success', 'error', 'warning', 'info')
        :param timeout: Auto-dismiss timeout in seconds
        """
        super().__init__(
            orientation='horizontal',
            size_hint=(0.8, None),
            height=dp(60),
            spacing=dp(10),
            padding=dp(15),
            **kwargs
        )
        
        self.notification_type = notification_type
        
        # Create message label
        message_label = Label(
            text=message,
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        
        # Create close button
        close_button = Button(
            text='×',
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'center_y': 0.5}
        )
        close_button.bind(on_press=self._on_close)
        
        # Add widgets
        self.add_widget(message_label)
        self.add_widget(close_button)
        
        # Apply styling
        self._apply_styling()
        
        # Schedule auto-dismiss
        if timeout > 0:
            Clock.schedule_once(self._auto_dismiss, timeout)
        
        Logger.info(f'NotificationToast: Created {notification_type} toast: {message}')
    
    def _apply_styling(self):
        """Apply background color based on notification type."""
        background_colors = {
            'success': (0.2, 0.8, 0.2, 0.9),  # Green
            'error': (0.8, 0.2, 0.2, 0.9),    # Red
            'warning': (0.8, 0.6, 0.2, 0.9),  # Orange
            'info': (0.2, 0.4, 0.8, 0.9)      # Blue
        }
        
        # Note: In a real implementation, you'd set canvas instructions here
        # For now, we'll rely on the parent container to handle styling
        self.background_color = background_colors.get(self.notification_type, 
                                                     background_colors['info'])
    
    def _on_close(self, button):
        """Handle close button press."""
        self._remove_from_parent()
    
    def _auto_dismiss(self, dt):
        """Auto-dismiss the toast after timeout."""
        self._remove_from_parent()
    
    def _remove_from_parent(self):
        """Remove this toast from its parent container."""
        if self.parent:
            self.parent.remove_widget(self)
            Logger.info(f'NotificationToast: Removed {self.notification_type} toast')
