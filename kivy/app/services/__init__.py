"""
Services package - Background services and utilities

This package contains:
- AppStateManager: Application state management
- FileManager: File operations and CSV export/import
- NotificationService: Cross-platform notifications
- SchedulerService: Background task scheduling
- ThemeManager: UI theme management
"""

from .app_state_manager import AppStateManager
from .file_manager import FileManager

__all__ = ['AppStateManager', 'FileManager'] 