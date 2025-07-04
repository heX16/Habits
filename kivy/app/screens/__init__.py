"""
Screens package - UI screens and navigation

This package contains:
- MainTrackerScreen: Main habit tracking interface
- OptionsScreen: Settings and habit management
- HabitDetailScreen: Individual habit calendar view
- HabitEditScreen: Habit parameter editing
"""

# Screens module for Habits Kivy app
from .main_tracker_screen import MainTrackerScreen
from .options_screen import OptionsScreen
from .habit_edit_screen import HabitEditScreen
from .habit_detail_screen import HabitDetailScreen

__all__ = ['MainTrackerScreen', 'OptionsScreen', 'HabitEditScreen', 'HabitDetailScreen'] 