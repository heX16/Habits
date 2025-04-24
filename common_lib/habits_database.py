import sqlite3
from datetime import date, datetime, timedelta
import csv
import os
from typing import Optional, Union
from pathlib import Path
from os import PathLike

# Status constants
class HabitStatus:
    NOT_SET = 0
    DONE_MINI = 1
    DONE = 2
    DONE_ELITE = 3
    FAIL = 9
    NUMBER_0 = 10
    NUMBER_1 = 11
    NUMBER_2 = 12
    NUMBER_3 = 13
    NUMBER_4 = 14
    NUMBER_5 = 15
    NUMBER_6 = 16
    NUMBER_7 = 17
    NUMBER_8 = 18
    NUMBER_9 = 19

class HabitsDatabase:
    '''
    Database class for managing habits, habit tracking, and special parameters.
    '''

    # Special habit_id value for global parameters
    GLOBAL_PARAMS = -1

    # Parameters that can be set for individual habits
    VALID_HABIT_PARAMS = {'fail_by_default', 'single_checkbox', 'multi_numbers', 'bad_habit'}

    # Parameters that can only be set globally
    VALID_GLOBAL_PARAMS = {
        'theme',        # UI theme (light/dark) (work in progress)
        'test_option'   # Test parameter used in options page (test, will be removed)
    }

    @staticmethod
    def str_to_date(date_str: str) -> date:
        """Convert a string in format 'YYYY-MM-DD' to a date object"""
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    def __init__(self, db_path: Union[str, PathLike[str]], create_tables_if_missing=True, clear_tables_if_missing=False, create_db_file_if_missing=True):
        '''
        Initialize the Database object and create tables if they do not exist.

        :param db_path: Path to the SQLite database file
        :param create_tables_if_missing: Whether to create tables if they don't exist (default: True)
        :param clear_tables_if_missing: Whether to clear existing tables if some are missing (default: False)
        :param create_db_file_if_missing: Whether to create database file if it doesn't exist (default: True)
        '''
        self.db_path = Path(db_path)
        self.create_tables_if_missing = create_tables_if_missing
        self.clear_tables_if_missing = clear_tables_if_missing
        self.create_db_file_if_missing = create_db_file_if_missing
        self.init_db()

    def connect(self):
        '''
        Create and return a new database connection.
        '''
        if not self.create_db_file_if_missing and not self.db_path.exists():
            raise FileNotFoundError(f"Database file does not exist: {self.db_path}")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        '''
        Initialize the database with the required tables.
        If any required table is missing and create_tables_if_missing is True,
        either clear database and create all tables (if clear_tables_if_missing is True),
        or raise an exception (if clear_tables_if_missing is False).
        '''
        conn = self.connect()
        cursor = conn.cursor()

        # Check if all required tables exist
        cursor.execute('''SELECT name FROM sqlite_master
                         WHERE type='table' AND
                         name IN ('habits_list', 'habit_tracking', 'habit_params')''')
        existing_tables = {row['name'] for row in cursor.fetchall()}

        required_tables = {'habits_list', 'habit_tracking', 'habit_params'}

        conn.close()

        # If tables are missing, handle according to parameters
        if not required_tables.issubset(existing_tables):
            if self.clear_tables_if_missing:
                # Clear and recreate all tables
                self.clear_db()
                self.create_tables()
            else:
                missing_tables = required_tables - existing_tables
                if not self.create_tables_if_missing:
                    raise Exception(f"Required tables are missing: {missing_tables}")

                self.create_tables()


    def create_tables(self):
        '''
        Create all necessary tables in the database.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        try:
            conn.execute('BEGIN TRANSACTION')

            cursor.execute('CREATE TABLE habits_list ('
                         'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                         'name TEXT NOT NULL UNIQUE, '
                         'sequence INTEGER NOT NULL DEFAULT 0)')

            cursor.execute('CREATE TABLE habit_tracking ('
                         'habit_id INTEGER, '
                         'date TEXT NOT NULL, '
                         'status INTEGER DEFAULT 0, '
                         'PRIMARY KEY (habit_id, date), '
                         'FOREIGN KEY (habit_id) REFERENCES habits_list(id))')

            cursor.execute('CREATE TABLE habit_params ('
                         'habit_id INTEGER, '
                         'param_name TEXT NOT NULL, '
                         'value TEXT NOT NULL, '
                         'PRIMARY KEY (habit_id, param_name))')

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise Exception(f'Error creating tables: {str(e)}')

        finally:
            conn.close()

    def clear_db(self):
        '''
        Clear all tables from the database.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        try:
            conn.execute('BEGIN TRANSACTION')

            # Drop all tables
            cursor.execute('DROP TABLE IF EXISTS habit_tracking')
            cursor.execute('DROP TABLE IF EXISTS habit_params')
            cursor.execute('DROP TABLE IF EXISTS habits_list')

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise Exception(f'Error clearing database: {str(e)}')

        finally:
            conn.close()

    def add_habit(self, name):
        '''
        Add a new habit.

        :param name: The name of the habit.
        :return: The ID of the newly added habit.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Get maximum sequence
            cursor.execute('SELECT MAX(sequence) as max_seq FROM habits_list')
            max_seq = cursor.fetchone()['max_seq']
            new_sequence = (max_seq or 0) + 10

            cursor.execute('INSERT INTO habits_list (name, sequence) VALUES (?, ?)',
                         (name, new_sequence))
            conn.commit()
            habit_id = cursor.lastrowid
            return habit_id
        finally:
            conn.close()

    def delete_habit(self, habit_id):
        '''
        Delete a habit and its associated tracking data and parameters.

        :param habit_id: The ID of the habit to delete.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM habit_tracking WHERE habit_id = ?', (habit_id,))
        cursor.execute('DELETE FROM habit_params WHERE habit_id = ?', (habit_id,))
        cursor.execute('DELETE FROM habits_list WHERE id = ?', (habit_id,))
        conn.commit()
        conn.close()

    def update_habit(self, habit_id, date, status):
        '''
        Update the status of a habit for a given date.
        If status is 0, the record will be deleted from the database.

        :param habit_id: The ID of the habit.
        :param date: The date in 'YYYY-MM-DD' format.
        :param status: The new status value.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        try:
            if status == 0:
                cursor.execute('''DELETE FROM habit_tracking
                                WHERE habit_id = ? AND date = ?''',
                             (habit_id, date))
            else:
                cursor.execute('''INSERT INTO habit_tracking (habit_id, date, status)
                                VALUES (?, ?, ?)
                                ON CONFLICT(habit_id, date)
                                DO UPDATE SET status=excluded.status''',
                             (habit_id, date, status))
            conn.commit()
        finally:
            conn.close()

    def status_mapping(self, value: int, habit_id: int, fail_by_default: bool = False,
                      first_tracking_date: Optional[date] = None, current_date: Optional[date] = None,
                      today: Optional[date] = None, single_checkbox: bool = False,
                      multi_numbers: bool = False) -> int:
        '''
        Maps database status values to client-side values.
        Takes into account habit's fail_by_default parameter.

        :param value: The status value from database
        :param habit_id: The ID of the habit
        :param fail_by_default: The fail_by_default parameter value ('0' or '1')
        :param first_tracking_date: first tracking date for the habit
        :param current_date: Current date being processed
        :param today: Today's date (for future date checks)
        :param single_checkbox: Whether the habit uses only a single checkbox
        :param multi_numbers: Whether the habit uses only numbers (0, 10-19)
        :return: Mapped status value for client
        '''
        # New numeric statuses (10-19) don't change with single_checkbox
        if value >= HabitStatus.NUMBER_0 and value <= HabitStatus.NUMBER_9:
            return value

        # If multi_numbers is enabled and value is not numeric (0, 10-19), map to 0
        if multi_numbers and not (value == HabitStatus.NOT_SET or (value >= HabitStatus.NUMBER_0 and value <= HabitStatus.NUMBER_9)):
            return HabitStatus.NOT_SET

        # If single_checkbox is enabled, map all "done" statuses to 2 ("done")
        if single_checkbox and value in [HabitStatus.DONE_MINI, HabitStatus.DONE_ELITE]:  # If status is "done mini" or "done elite"
            return HabitStatus.DONE  # Return "done"

        if fail_by_default:
            if value == HabitStatus.NOT_SET and current_date and today and first_tracking_date:
                # If status is `NOT_SET` (0) and
                # current date is between:
                # - first tracking date (not including) and
                # - today (not including)
                # Then return `FAIL`` (9)
                if first_tracking_date < current_date < today:
                    return HabitStatus.FAIL
                return HabitStatus.NOT_SET

        return value

    def get_habits_list(self, habit_id=None):
        '''
        Retrieve a list of all habits or a specific habit.

        :param habit_id: Optional habit ID to fetch a specific habit
        :return: A list of dictionaries, each containing the habit ID and name.
        :raises: Exception if habit_id provided but not found
        '''
        conn = self.connect()
        cursor = conn.cursor()

        if habit_id:
            cursor.execute('SELECT id, name, sequence FROM habits_list WHERE id = ?', (habit_id,))
            habits = cursor.fetchall()
            if not habits:
                conn.close()
                raise Exception(f'Habit with id {habit_id} not found')
        else:
            cursor.execute('SELECT id, name, sequence FROM habits_list ORDER BY sequence, id')
            habits = cursor.fetchall()

        habits_list = [{'id': habit['id'], 'name': habit['name'], 'sequence': habit['sequence']} for habit in habits]
        conn.close()
        return habits_list

    def fetch_habit(self, habit, start_date, end_date, cursor, today=None):
        '''
        Fetch tracking data for a single habit.

        :param habit: Dictionary containing habit info (id and name) or habit ID
        :param start_date: The start date as 'YYYY-MM-DD'
        :param end_date: The end date as 'YYYY-MM-DD'
        :param cursor: Database cursor
        :param today: Current date for status mapping
        :return: Dictionary with habit data and tracking

        Return dict:
        ```
        {
        "id": 1,
        "name": "Test",
        "single_checkbox": false,
        "multi_numbers": false,
        "bad_habit": false,
        "tracking": [9,9,9,9,0,0,0,0,0,0]
        }
        ```
        '''
        # Handle both habit dict and habit id
        if isinstance(habit, dict):
            habit_id_val = habit['id']
            habit_name = habit['name']
        else:
            # Backwards compatibility - if habit ID is passed
            habits = self.get_habits_list(habit)
            if not habits:
                return None
            habit_id_val = habits[0]['id']
            habit_name = habits[0]['name']

        # Generate date list
        start_dt = self.str_to_date(start_date)
        end_dt = self.str_to_date(end_date)
        num_days = (end_dt - start_dt).days + 1
        date_list = [start_dt + timedelta(days=i) for i in range(num_days)]

        # Get fail_by_default parameter for this habit
        fail_by_default: bool = self.get_param(habit_id_val, 'fail_by_default', '0') == '1'

        # Get single_checkbox parameter for this habit
        single_checkbox: bool = self.get_param(habit_id_val, 'single_checkbox', '0') == '1'

        # Get multi_numbers parameter for this habit
        multi_numbers: bool = self.get_param(habit_id_val, 'multi_numbers', '0') == '1'

        # Get bad_habit parameter for this habit
        bad_habit: bool = self.get_param(habit_id_val, 'bad_habit', '0') == '1'

        # Get last tracking date if fail_by_default is enabled
        first_tracking_date = self.get_first_tracking_date(habit_id_val)

        # Get all records for habit in date range, ordered by date
        cursor.execute('''SELECT date, status
                        FROM habit_tracking
                        WHERE habit_id = ? AND date BETWEEN ? AND ?
                        ORDER BY date''',
                     (habit_id_val, start_date, end_date))

        tracking_rows = cursor.fetchall()
        tracking_dict = {self.str_to_date(row['date']): row['status']
                        for row in tracking_rows}

        tracking = []
        for current_date in date_list:
            status = tracking_dict.get(current_date, 0)
            status = self.status_mapping(
                status,
                habit_id_val,
                fail_by_default=fail_by_default,
                first_tracking_date=first_tracking_date,
                current_date=current_date,
                today=today,  # Pass today's date
                single_checkbox=single_checkbox,
                multi_numbers=multi_numbers
            )
            tracking.append(status)

        return {
            'id': habit_id_val,
            'name': habit_name,
            'single_checkbox': single_checkbox,
            'multi_numbers': multi_numbers,
            'first_tracking_date': first_tracking_date,
            'bad_habit': bad_habit,
            'tracking': tracking,
        }

    def fetch_habits(self, start_date, end_date, habit_id=None, today=None):
        '''
        Fetch habits and their tracking data within a specified date range.

        :param start_date: The start date as 'YYYY-MM-DD'
        :param end_date: The end date as 'YYYY-MM-DD'
        :param habit_id: Optional habit ID to fetch a specific habit
        :param today: Current date for status mapping
        :return: A dictionary containing the start_date, end_date, and a list of habits with tracking data
        :raises ValueError: If the date format is invalid

        Return dict:
        ```
        {
        "end_date": "2025-03-30",
        "start_date": "2025-03-21",
        "habits": [
            {
            "id": 1,
            "name": "Test",
            "tracking": [9,9,9,9,0,0,0,0,0,0]
            },
            ...
        ]
        }
        ```
        '''
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD.')

        num_days = (end_dt - start_dt).days + 1
        date_list = [(start_dt + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days)]

        conn = self.connect()
        cursor = conn.cursor()

        try:
            habits = self.get_habits_list(habit_id)
            habits_data = []

            for habit in habits:
                habit_data = self.fetch_habit(habit, start_date, end_date, cursor, today=today)
                if habit_data:
                    habits_data.append(habit_data)

        finally:
            conn.close()

        return {
            'start_date': start_date,
            'end_date': end_date,
            'habits': habits_data
        }

    def validate_param(self, param_name: str, habit_id: int, value: str = None) -> None:
        """
        Validate parameter name and check if it can be used with given habit_id.

        :param param_name: Name of the parameter
        :param habit_id: Habit ID or GLOBAL_PARAMS for global parameters
        :param value: Parameter value
        :raises ValueError: If parameter name is invalid for given habit_id
        """
        if habit_id == self.GLOBAL_PARAMS:
            if param_name not in self.VALID_GLOBAL_PARAMS:
                raise ValueError(f"Unknown global parameter: {param_name}")
        else:
            if param_name not in self.VALID_HABIT_PARAMS:
                raise ValueError(f"Unknown habit parameter: {param_name}")

    def get_param(self, habit_id, param_name, default_value=None):
        '''
        Get the value of a specific parameter for a habit or globally.

        :param habit_id: The habit ID (HabitsDatabase.GLOBAL_PARAMS for global parameters).
        :param param_name: The name of the parameter.
        :param default_value: Value to return if parameter is not found.
        :return: The value of the parameter, or default_value if not found.
        :raises ValueError: If parameter name is invalid for given habit_id
        '''
        self.validate_param(param_name, habit_id)

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM habit_params WHERE habit_id = ? AND param_name = ?',
                       (habit_id, param_name))
        row = cursor.fetchone()
        conn.close()

        return row['value'] if row else default_value

    def set_param(self, habit_id, param_name, value):
        '''
        Set or update the value of a specific parameter for a habit or globally.

        :param habit_id: The habit ID (HabitsDatabase.GLOBAL_PARAMS for global parameters).
        :param param_name: The name of the parameter.
        :param value: The value to store.
        :raises ValueError: If parameter name is invalid for given habit_id
        '''
        self.validate_param(param_name, habit_id, value)

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO habit_params (habit_id, param_name, value)
                          VALUES (?, ?, ?)
                          ON CONFLICT(habit_id, param_name) DO UPDATE SET value=excluded.value''',
                       (habit_id, param_name, value))
        conn.commit()
        conn.close()

    def export_to_csv(self):
        '''
        Generate CSV data for all habits in a human-readable format.
        Uses existing functions to get habits and parameters.

        :yield: Each line of CSV data as a string
        '''
        conn = self.connect()
        cursor = conn.cursor()

        try:
            # Export habits and their tracking data
            habits = self.get_habits_list()
            for habit in habits:
                yield f'habit:,{habit["name"]},{habit["sequence"]}'

                # Export tracking data for this habit - direct database query
                cursor.execute('''SELECT date, status
                                FROM habit_tracking
                                WHERE habit_id = ?
                                ORDER BY date''',
                             (habit['id'],))

                for track in cursor:
                    yield f'{track["date"]},{track["status"]}'

                yield ''

            # Export all parameters (global and habit-specific)
            habits_with_global = [{'id': -1, 'name': 'global'}] + habits
            for habit in habits_with_global:
                cursor.execute('SELECT param_name, value FROM habit_params WHERE habit_id = ?',
                             (habit['id'],))
                first_param = cursor.fetchone()
                if first_param:
                    yield f'habit_params:,{habit["name"]}'
                    yield f'{first_param["param_name"]},{first_param["value"]}'
                    for param in cursor:
                        yield f'{param["param_name"]},{param["value"]}'
                    yield ''

        finally:
            conn.close()

    def import_from_csv(self, csv_lines):
        '''
        Import habits data from CSV lines in human-readable format.

        :param csv_lines: Iterator of CSV lines
        :raises Exception: If there is an error during import
        '''
        conn = self.connect()
        cursor = conn.cursor()

        try:
            conn.execute('BEGIN TRANSACTION')

            # Clear and recreate tables
            self.clear_db()
            self.create_tables()

            current_habit_id = None
            mode = None  # Can be 'habit' or 'params'
            habits_dict = {}  # Cache for habit name -> id mapping

            for line in csv_lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                # Split CSV line manually to handle quoted values
                row = next(csv.reader([line]))

                if line.startswith('habit:'):
                    # New habit section
                    _, habit_name, habit_sequence = row
                    current_habit_id = self.add_habit(habit_name)
                    self.set_habit_sequence(current_habit_id, habit_sequence)
                    habits_dict[habit_name] = current_habit_id
                    mode = 'habit'

                elif line.startswith('habit_params:'):
                    # New parameters section
                    _, target = row
                    mode = 'params'
                    if target == 'global':
                        current_habit_id = self.GLOBAL_PARAMS
                    else:
                        # Find habit ID by name from our cache
                        current_habit_id = habits_dict.get(target)
                        if current_habit_id is None:
                            mode = None

                elif mode == 'habit':
                    # Tracking data line
                    date, status = row
                    self.update_habit(current_habit_id, date, int(status))

                elif mode == 'params':
                    # Parameter line
                    param_name, value = row
                    self.set_param(current_habit_id, param_name, value)

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise Exception(f'Error during import: {str(e)}')

        finally:
            conn.close()

    def get_status_options(self):
        '''
        Returns dictionary of status options for habits.
        The 'all' key contains a list of all available statuses.
        '''
        return {
            'all': [
                {'value': HabitStatus.NOT_SET, 'label': 'not set',    'icon': ' ',  'color': 'none', 'as_char': ' ', 'image': 'empty.png'},
                {'value': HabitStatus.DONE_MINI, 'label': 'done mini',  'icon': '☑️', 'color': 'green', 'as_char': 'v', 'image': 'done_mini.png'},
                {'value': HabitStatus.DONE, 'label': 'done',       'icon': '✅', 'color': 'green', 'as_char': 'V', 'image': 'done.png'},
                {'value': HabitStatus.DONE_ELITE, 'label': 'done elite', 'icon': '🌟', 'color': 'gold', 'as_char': 'W', 'image': 'done_elite.png'},
                {'value': HabitStatus.FAIL, 'label': 'fail',       'icon': '❌', 'color': 'red', 'as_char': 'X', 'image': 'fail.png'},
            ],
            # good habits
            'gh1': [
                {'value': HabitStatus.NOT_SET, 'label': 'not set', 'icon': ' ', 'color': 'none', 'as_char': ' ', 'image': 'empty.png'},
                {'value': HabitStatus.DONE_MINI, 'label': 'done', 'icon': '✅', 'color': 'green', 'as_char': 'V', 'image': 'done.png'},
                {'value': HabitStatus.DONE, 'label': 'fail', 'icon': '❌', 'color': 'red', 'as_char': 'X', 'image': 'fail.png'},
            ],
            'gh3': [
                {'value': HabitStatus.NOT_SET, 'label': 'not set',    'icon': ' ',  'color': 'none', 'as_char': ' ', 'image': 'empty.png'},
                {'value': HabitStatus.DONE_MINI, 'label': 'done mini',  'icon': '☑️', 'color': 'green', 'as_char': 'v', 'image': 'done_mini.png'},
                {'value': HabitStatus.DONE, 'label': 'done',       'icon': '✅', 'color': 'green', 'as_char': 'V', 'image': 'done.png'},
                {'value': HabitStatus.DONE_ELITE, 'label': 'done elite', 'icon': '🌟', 'color': 'gold', 'as_char': 'W', 'image': 'done_elite.png'},
                {'value': HabitStatus.FAIL, 'label': 'fail',       'icon': '❌', 'color': 'red', 'as_char': 'X', 'image': 'fail.png'},
            ],
            'gh10': [
                {'value': HabitStatus.NUMBER_0, 'label': '0',  'icon': '0️⃣', 'color': 'green', 'as_char': '0', 'image': 'number_0.png'},
                {'value': HabitStatus.NUMBER_1, 'label': '1',  'icon': '1️⃣', 'color': 'green', 'as_char': '1', 'image': 'number_1.png'},
                {'value': HabitStatus.NUMBER_2, 'label': '2',  'icon': '2️⃣', 'color': 'green', 'as_char': '2', 'image': 'number_2.png'},
                {'value': HabitStatus.NUMBER_3, 'label': '3',  'icon': '3️⃣', 'color': 'green', 'as_char': '3', 'image': 'number_3.png'},
                {'value': HabitStatus.NUMBER_4, 'label': '4',  'icon': '4️⃣', 'color': 'green', 'as_char': '4', 'image': 'number_4.png'},
                {'value': HabitStatus.NUMBER_5, 'label': '5',  'icon': '5️⃣', 'color': 'green', 'as_char': '5', 'image': 'number_5.png'},
                {'value': HabitStatus.NUMBER_6, 'label': '6',  'icon': '6️⃣', 'color': 'green', 'as_char': '6', 'image': 'number_6.png'},
                {'value': HabitStatus.NUMBER_7, 'label': '7',  'icon': '7️⃣', 'color': 'green', 'as_char': '7', 'image': 'number_7.png'},
                {'value': HabitStatus.NUMBER_8, 'label': '8',  'icon': '8️⃣', 'color': 'green', 'as_char': '8', 'image': 'number_8.png'},
                {'value': HabitStatus.NUMBER_9, 'label': '9',  'icon': '9️⃣', 'color': 'green', 'as_char': '9', 'image': 'number_9.png'},
            ],
            # bad habits
            'bh1': [
                {'value': HabitStatus.NOT_SET, 'label': 'not set', 'icon': ' ', 'color': 'none', 'as_char': ' ', 'image': 'empty.png'},
                {'value': HabitStatus.DONE_MINI, 'label': 'done', 'icon': '✅', 'color': 'green', 'as_char': 'V', 'image': 'done.png'},
                {'value': HabitStatus.DONE, 'label': 'fail', 'icon': '❌', 'color': 'red', 'as_char': 'X', 'image': 'fail.png'},
            ],
            'bh3': [
                {'value': HabitStatus.NOT_SET, 'label': 'not set',    'icon': ' ',  'color': 'none', 'as_char': ' ', 'image': 'empty.png'},
                {'value': HabitStatus.DONE_MINI, 'label': 'low fail',   'icon': '🟡', 'color': 'yellow', 'as_char': '~', 'image': 'yellow_circle.png'},
                {'value': HabitStatus.DONE, 'label': 'medium fail','icon': '🟠', 'color': 'orange', 'as_char': 'x', 'image': 'orange_circle.png'},
                {'value': HabitStatus.DONE_ELITE, 'label': 'high fail',  'icon': '🔴', 'color': 'red', 'as_char': 'X', 'image': 'red_circle.png'},
                {'value': HabitStatus.FAIL, 'label': 'success',    'icon': '✅', 'color': 'green', 'as_char': 'V', 'image': 'done.png'},
            ],

        }

    def rename_habit(self, habit_id, new_name):
        '''
        Rename a habit.

        :param habit_id: The ID of the habit to rename
        :param new_name: New name for the habit
        :raises Exception: If habit not found or name already exists
        '''
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Check if habit exists
            cursor.execute('SELECT id FROM habits_list WHERE id = ?', (habit_id,))
            if not cursor.fetchone():
                raise Exception(f'Habit with id {habit_id} not found')

            # Check if new name already exists
            cursor.execute('SELECT id FROM habits_list WHERE name = ? AND id != ?',
                          (new_name, habit_id))
            if cursor.fetchone():
                raise Exception(f'Habit with name "{new_name}" already exists')

            # Update habit name
            cursor.execute('UPDATE habits_list SET name = ? WHERE id = ?',
                          (new_name, habit_id))
            conn.commit()

        finally:
            conn.close()

    def get_first_tracking_date(self, habit_id, last_date: bool = False) -> Optional[date]:
        '''
        Get first or last tracking date for habit
        :return: date object or None
        '''
        conn = self.connect()
        cursor = conn.cursor()
        sort_order = 'DESC' if last_date else 'ASC'
        try:
            cursor.execute(f'''SELECT date FROM habit_tracking
                            WHERE habit_id = ?
                            ORDER BY date {sort_order}
                            LIMIT 1''', (habit_id,))
            row = cursor.fetchone()
            if not row:
                return None
            try:
                return self.str_to_date(row['date'])
            except ValueError:
                return None
        finally:
            conn.close()

    def get_last_tracking_date(self, habit_id) -> Optional[date]:
        '''Get last tracking date'''
        return self.get_first_tracking_date(habit_id, last_date=True)

    def get_tracking_count(self):
        """
        Get total number of tracking records.

        :return: Number of records in habit_tracking table
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) as count FROM habit_tracking')
            result = cursor.fetchone()
            return result['count']
        finally:
            conn.close()

    def is_readonly(self) -> bool:
        """
        Check if database is in read-only mode by checking file permissions.

        :return: True if database is read-only, False otherwise
        """
        return not os.access(self.db_path, os.W_OK)

    def set_habit_sequence(self, habit_id, sequence):
        '''
        Set sequence number for a habit.

        :param habit_id: The ID of the habit
        :param sequence: New sequence number
        :raises Exception: If habit not found
        '''
        conn = self.connect()
        cursor = conn.cursor()
        try:
            # Check if habit exists
            cursor.execute('SELECT id FROM habits_list WHERE id = ?', (habit_id,))
            if not cursor.fetchone():
                raise Exception(f'Habit with id {habit_id} not found')

            # Update sequence
            cursor.execute('UPDATE habits_list SET sequence = ? WHERE id = ?',
                          (sequence, habit_id))
            conn.commit()

        finally:
            conn.close()

    def reorder_habit(self, habit_id, direction):
        '''
        Change habit sequence by moving it up or down in the list.

        :param habit_id: The ID of the habit to reorder
        :param direction: Direction to move ('up' or 'down')
        :raises Exception: If habit not found or cannot be moved in specified direction
        '''
        # Get ordered list of habits
        habits = self.get_habits_list()

        # Find current habit index
        current_index = -1
        for i, habit in enumerate(habits):
            if habit['id'] == habit_id:
                current_index = i
                break

        if current_index == -1:
            raise Exception(f'Habit with id {habit_id} not found')

        # Check if we can move in specified direction
        if direction == 'up' and current_index == 0:
            raise Exception('Cannot move first habit up')
        if direction == 'down' and current_index == len(habits) - 1:
            raise Exception('Cannot move last habit down')

        # Calculate target index
        target_index = current_index - 1 if direction == 'up' else current_index + 1

        # Swap sequences
        current_sequence = habits[current_index]['sequence']
        target_sequence = habits[target_index]['sequence']

        # Check if sequences are equal, try fix it (not ideal, but it works)
        if current_sequence == target_sequence:
            current_sequence += 1

        self.set_habit_sequence(habit_id, target_sequence)
        self.set_habit_sequence(habits[target_index]['id'], current_sequence)


