"""
Notification Service

Provides a centralized service for managing notifications across the entire application.
Handles popup notifications, toast messages, and status updates.
"""

from typing import Optional, Dict, Any
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.app import App

from ..widgets.notification_popup import NotificationPopup, NotificationToast


class NotificationService:
    """
    Centralized notification service for the entire application.
    
    Provides methods to show different types of notifications:
    - Popup notifications (modal)
    - Toast notifications (non-intrusive)
    - Status bar updates
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern - ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the notification service."""
        if self._initialized:
            return
            
        self._initialized = True
        self.toast_container = None
        self.active_notifications = []
        
        Logger.info('NotificationService: Initialized')
    
    def show_success(self, message: str, title: str = None, 
                    use_popup: bool = True, timeout: float = 5.0) -> None:
        """
        Show a success notification.
        
        :param message: Success message to display
        :param title: Optional title (auto-generated if None)
        :param use_popup: True for popup, False for toast
        :param timeout: Auto-dismiss timeout in seconds
        """
        self._show_notification(message, 'success', title, use_popup, timeout)
    
    def show_error(self, message: str, title: str = None, 
                  use_popup: bool = True, timeout: float = 8.0) -> None:
        """
        Show an error notification.
        
        :param message: Error message to display
        :param title: Optional title (auto-generated if None)
        :param use_popup: True for popup, False for toast
        :param timeout: Auto-dismiss timeout in seconds (longer for errors)
        """
        self._show_notification(message, 'error', title, use_popup, timeout)
    
    def show_warning(self, message: str, title: str = None, 
                    use_popup: bool = True, timeout: float = 6.0) -> None:
        """
        Show a warning notification.
        
        :param message: Warning message to display
        :param title: Optional title (auto-generated if None)
        :param use_popup: True for popup, False for toast
        :param timeout: Auto-dismiss timeout in seconds
        """
        self._show_notification(message, 'warning', title, use_popup, timeout)
    
    def show_info(self, message: str, title: str = None, 
                 use_popup: bool = False, timeout: float = 4.0) -> None:
        """
        Show an info notification.
        
        :param message: Info message to display
        :param title: Optional title (auto-generated if None)
        :param use_popup: True for popup, False for toast (default: toast for info)
        :param timeout: Auto-dismiss timeout in seconds
        """
        self._show_notification(message, 'info', title, use_popup, timeout)
    
    def _show_notification(self, message: str, notification_type: str, 
                          title: str = None, use_popup: bool = True, 
                          timeout: float = 5.0) -> None:
        """
        Internal method to show a notification.
        
        :param message: Message to display
        :param notification_type: Type of notification
        :param title: Optional title
        :param use_popup: True for popup, False for toast
        :param timeout: Auto-dismiss timeout
        """
        try:
            if use_popup:
                self._show_popup_notification(message, notification_type, title, timeout)
            else:
                self._show_toast_notification(message, notification_type, timeout)
                
        except Exception as e:
            Logger.error(f'NotificationService: Error showing notification: {e}')
            # Fallback to console logging
            Logger.info(f'NotificationService: [{notification_type.upper()}] {message}')
    
    def _show_popup_notification(self, message: str, notification_type: str, 
                                title: str = None, timeout: float = 5.0) -> None:
        """Show a popup notification."""
        popup = NotificationPopup(
            message=message,
            notification_type=notification_type,
            title=title,
            timeout=timeout
        )
        
        popup.open()
        self.active_notifications.append(popup)
        
        # Remove from active list when dismissed
        def on_dismiss(popup_instance):
            if popup_instance in self.active_notifications:
                self.active_notifications.remove(popup_instance)
        
        popup.bind(on_dismiss=on_dismiss)
        
        Logger.info(f'NotificationService: Showed popup {notification_type}: {message}')
    
    def _show_toast_notification(self, message: str, notification_type: str, 
                                timeout: float = 4.0) -> None:
        """Show a toast notification."""
        # Get the current app and root widget
        app = App.get_running_app()
        if not app or not app.root:
            Logger.warning('NotificationService: No app root available for toast')
            return
        
        # Create toast
        toast = NotificationToast(
            message=message,
            notification_type=notification_type,
            timeout=timeout
        )
        
        # TODO: Add toast to a container at the top of the screen
        # For now, we'll fall back to popup for toast notifications
        # This would require a dedicated toast container in the main app layout
        
        Logger.info(f'NotificationService: Toast {notification_type}: {message}')
        Logger.warning('NotificationService: Toast display not fully implemented, using popup fallback')
        
        # Fallback to popup with shorter timeout
        self._show_popup_notification(message, notification_type, None, min(timeout, 3.0))
    
    def dismiss_all(self) -> None:
        """Dismiss all active notifications."""
        for notification in self.active_notifications[:]:  # Copy list to avoid modification during iteration
            if hasattr(notification, 'dismiss'):
                notification.dismiss()
        
        self.active_notifications.clear()
        Logger.info('NotificationService: Dismissed all notifications')
    
    def update_status_bar(self, screen_name: str, message: str) -> None:
        """
        Update the status bar of a specific screen.
        
        :param screen_name: Name of the screen to update
        :param message: Status message
        """
        try:
            app = App.get_running_app()
            if not app or not hasattr(app, 'screen_manager'):
                Logger.warning('NotificationService: No screen manager available')
                return
            
            screen = app.screen_manager.get_screen(screen_name)
            
            # Try different status update methods based on screen type
            if hasattr(screen, 'update_status_bar'):
                screen.update_status_bar(message)
            elif hasattr(screen, 'update_status'):
                screen.update_status(message)
            elif hasattr(screen, 'show_status'):
                screen.show_status(message, 'info')
            else:
                Logger.warning(f'NotificationService: No status method found for screen {screen_name}')
                
        except Exception as e:
            Logger.error(f'NotificationService: Error updating status bar: {e}')
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the notification service."""
        return {
            'active_notifications': len(self.active_notifications),
            'service_initialized': self._initialized
        }


# Global instance for easy access
notifications = NotificationService()


# Convenience functions for easy access throughout the app
def show_success(message: str, **kwargs) -> None:
    """Show a success notification."""
    notifications.show_success(message, **kwargs)


def show_error(message: str, **kwargs) -> None:
    """Show an error notification."""
    notifications.show_error(message, **kwargs)


def show_warning(message: str, **kwargs) -> None:
    """Show a warning notification."""
    notifications.show_warning(message, **kwargs)


def show_info(message: str, **kwargs) -> None:
    """Show an info notification."""
    notifications.show_info(message, **kwargs)


def dismiss_all_notifications() -> None:
    """Dismiss all active notifications."""
    notifications.dismiss_all()


def update_status(screen_name: str, message: str) -> None:
    """Update status bar of a specific screen."""
    notifications.update_status_bar(screen_name, message)
