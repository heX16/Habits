"""
Models package - Database and domain logic

This package contains:
- Database connection and operations
- Business logic classes
- Data validation and transformation
"""

# Models module for Habits Kivy app
from .habits_model import HabitsModel
from .date_calculator import DateCalculator

__all__ = ['HabitsModel', 'DateCalculator'] 