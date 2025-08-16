"""
Services package - Background services and utilities

This package contains:
- AppStateManager: Application state management
- FileManager: File operations and CSV export/import
- [NotificationManager moved to widgets for simplicity]
- SchedulerService: Background task scheduling
- ThemeManager: UI theme management
"""

from .app_state_manager import AppStateManager
from .file_manager import FileManager
# Notification service removed - using simple NotificationManager from widgets

__all__ = [
    'AppStateManager', 'FileManager'
] 