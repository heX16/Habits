"""
Notification Manager - Direct port from web version

Simple notification system identical to web/static/notifications.js
Shows toast-style notifications in top-right corner with auto-dismiss.
"""

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.app import App


class NotificationManager:
    """
    Direct port of NotificationManager from web version.
    
    Usage (same as web):
        notifications = NotificationManager()
        notifications.show("Error message")  # defaults to 'error'
        notifications.show("Success!", "success")
        notifications.show("Warning", "warning")
    """
    
    def __init__(self):
        self.container = self.create_container()
    
    def create_container(self):
        """Create notification container (equivalent to createContainer() in JS)"""
        app = App.get_running_app()
        if not app or not app.root:
            Logger.warning('NotificationManager: No app root available')
            return None
        
        # Create container widget that will hold notifications
        container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint=(None, None),
            width=dp(300),
            pos_hint={'right': 0.98, 'top': 0.95}
        )
        
        # Add to root widget
        app.root.add_widget(container)
        Logger.info('NotificationManager: Container created')
        return container
    
    def show(self, message, notification_type='error'):
        """
        Show notification (equivalent to show() in JS)
        
        :param message: Message text to display
        :param notification_type: 'error', 'success', 'warning'
        """
        if not self.container:
            Logger.warning('NotificationManager: No container available')
            return None
        
        # Create notification widget
        notification = self._create_notification_widget(message, notification_type)
        
        # Add to container
        self.container.add_widget(notification)
        
        # Auto-hide after 5 seconds (same as web version)
        Clock.schedule_once(lambda dt: self.hide(notification), 5.0)
        
        Logger.info(f'NotificationManager: Showed {notification_type}: {message}')
        return notification
    
    def _create_notification_widget(self, message, notification_type):
        """Create the notification widget with message and close button"""
        
        # Color scheme matching web version CSS
        colors = {
            'error': (0.8, 0.2, 0.2, 0.95),    # Red background
            'success': (0.2, 0.8, 0.2, 0.95), # Green background  
            'warning': (0.8, 0.6, 0.2, 0.95)  # Orange background
        }
        
        # Main notification layout
        notification = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=dp(60),
            padding=dp(15),
            spacing=dp(10)
        )
        
        # Apply background color
        with notification.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(*colors.get(notification_type, colors['error']))
            notification.bg_rect = RoundedRectangle(
                pos=notification.pos,
                size=notification.size,
                radius=[dp(8)]
            )
        
        # Update background when size/pos changes
        def update_bg(instance, value):
            notification.bg_rect.pos = instance.pos
            notification.bg_rect.size = instance.size
        
        notification.bind(pos=update_bg, size=update_bg)
        
        # Message text
        message_label = Label(
            text=message,
            color=(1, 1, 1, 1),  # White text
            text_size=(dp(220), None),
            halign='left',
            valign='middle'
        )
        
        # Close button (×)
        close_button = Button(
            text='×',
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            background_color=(0, 0, 0, 0),  # Transparent background
            color=(1, 1, 1, 1),  # White text
            font_size=dp(20)
        )
        close_button.bind(on_press=lambda btn: self.hide(notification))
        
        # Add widgets to notification
        notification.add_widget(message_label)
        notification.add_widget(close_button)
        
        return notification
    
    def hide(self, notification):
        """
        Hide notification (equivalent to hide() in JS)
        
        :param notification: Notification widget to hide
        """
        if not self.container or not notification:
            return
        
        # Simple immediate removal (web version has CSS animation, 
        # but for simplicity we'll just remove directly)
        if notification in self.container.children:
            self.container.remove_widget(notification)
            Logger.info('NotificationManager: Notification hidden')


# Global instance (same pattern as web version)
notifications = None


def get_notification_manager():
    """Get global notification manager instance"""
    global notifications
    if notifications is None:
        notifications = NotificationManager()
    return notifications
