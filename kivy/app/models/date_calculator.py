"""
Date Calculator

Utility class for date calculations, week navigation, and date range management.
Used by the main tracker for date-based operations.
"""

from datetime import date, datetime, timedelta
from typing import List, Tuple
from kivy.logger import Logger


class DateCalculator:
    """Utility class for date calculations and navigation"""
    
    @staticmethod
    def get_week_ending_sunday(target_date: date = None) -> Tuple[date, date]:
        """
        Get the week range ending on Sunday for a given date.
        
        :param target_date: Target date (default: today)
        :return: Tuple of (start_date, end_date) for the week
        """
        if target_date is None:
            target_date = date.today()
            
        # Find the Sunday of this week
        days_until_sunday = (6 - target_date.weekday()) % 7
        end_date = target_date + timedelta(days=days_until_sunday)
        
        # Start date is 6 days before Sunday
        start_date = end_date - timedelta(days=6)
        
        return start_date, end_date
        
    @staticmethod
    def get_previous_week(current_start: date, current_end: date) -> Tuple[date, date]:
        """
        Get the previous week range.
        
        :param current_start: Current week start date
        :param current_end: Current week end date
        :return: Tuple of (start_date, end_date) for previous week
        """
        new_end = current_start - timedelta(days=1)
        new_start = new_end - timedelta(days=6)
        return new_start, new_end
        
    @staticmethod
    def get_next_week(current_start: date, current_end: date) -> Tuple[date, date]:
        """
        Get the next week range.
        
        :param current_start: Current week start date
        :param current_end: Current week end date
        :return: Tuple of (start_date, end_date) for next week
        """
        new_start = current_end + timedelta(days=1)
        new_end = new_start + timedelta(days=6)
        return new_start, new_end
        
    @staticmethod
    def get_date_range_from_offset(date_offset: str = None) -> Tuple[date, date]:
        """
        Get date range from a date offset string.
        
        :param date_offset: Date string in YYYY-MM-DD format (default: today)
        :return: Tuple of (start_date, end_date) for the week containing the date
        """
        if date_offset:
            try:
                target_date = datetime.strptime(date_offset, '%Y-%m-%d').date()
            except ValueError:
                Logger.warning(f'DateCalculator: Invalid date format: {date_offset}, using today')
                target_date = date.today()
        else:
            target_date = date.today()
            
        return DateCalculator.get_week_ending_sunday(target_date)
        
    @staticmethod
    def get_date_headers(start_date: date, end_date: date) -> List[dict]:
        """
        Get list of date headers for the table.
        
        :param start_date: Start date of the range
        :param end_date: End date of the range
        :return: List of dictionaries with date information
        """
        headers = []
        current_date = start_date
        
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        while current_date <= end_date:
            headers.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_name': weekday_names[current_date.weekday()],
                'day_number': current_date.day,
                'month_name': current_date.strftime('%b'),
                'is_today': current_date == date.today(),
                'is_weekend': current_date.weekday() >= 5  # Saturday, Sunday
            })
            current_date += timedelta(days=1)
            
        return headers
        
    @staticmethod
    def get_week_label(start_date: date, end_date: date) -> str:
        """
        Get a label for the week range.
        
        :param start_date: Start date of the week
        :param end_date: End date of the week
        :return: String label for the week
        """
        today = date.today()
        
        # Check if this week contains today
        if start_date <= today <= end_date:
            return "This Week"
            
        # Check if it's next week
        next_week_start, next_week_end = DateCalculator.get_week_ending_sunday(today + timedelta(days=7))
        if start_date == next_week_start:
            return "Next Week"
            
        # Check if it's previous week
        prev_week_start, prev_week_end = DateCalculator.get_week_ending_sunday(today - timedelta(days=7))
        if start_date == prev_week_start:
            return "Previous Week"
            
        # Otherwise, show the date range
        if start_date.month == end_date.month:
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%d, %Y')}"
        else:
            return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
            
    @staticmethod
    def is_midnight_refresh_needed(last_refresh: datetime = None) -> bool:
        """
        Check if midnight refresh is needed.
        
        :param last_refresh: Last refresh datetime
        :return: True if refresh is needed
        """
        if last_refresh is None:
            return True
            
        now = datetime.now()
        
        # If last refresh was yesterday or earlier, we need to refresh
        if last_refresh.date() < now.date():
            return True
            
        return False
        
    @staticmethod
    def get_next_midnight() -> datetime:
        """
        Get the next midnight datetime.
        
        :return: Next midnight datetime
        """
        today = date.today()
        tomorrow = today + timedelta(days=1)
        return datetime.combine(tomorrow, datetime.min.time())
        
    @staticmethod
    def parse_date_string(date_str: str) -> date:
        """
        Parse a date string in YYYY-MM-DD format.
        
        :param date_str: Date string
        :return: Date object
        :raises ValueError: If date format is invalid
        """
        return datetime.strptime(date_str, '%Y-%m-%d').date()
        
    @staticmethod
    def format_date_string(date_obj: date) -> str:
        """
        Format a date object to YYYY-MM-DD string.
        
        :param date_obj: Date object
        :return: Formatted date string
        """
        return date_obj.strftime('%Y-%m-%d') 