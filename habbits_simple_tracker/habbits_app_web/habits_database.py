import sqlite3
from datetime import date, datetime, timedelta
import csv
import os
from typing import Optional

class HabitsDatabase:
    '''
    Database class for managing habits, habit tracking, and special parameters.
    '''
    # Special habit_id value for global parameters
    GLOBAL_PARAMS_ID = -1

    # Parameters that can be set for individual habits
    VALID_HABIT_PARAMS = {'fail_by_default', 'single_checkbox', 'multi_numbers', 'bad_habit'}

    # Parameters that can only be set globally
    VALID_GLOBAL_PARAMS = {
        'theme',        # UI theme (light/dark) (work in progress)
        'test_option'   # Test parameter used in options page (test, will be removed)
    }

    def __init__(self, db_path):
        '''
        Initialize the Database object and create tables if they do not exist.

        :param db_path: Path to the SQLite database file
        '''
        self.db_path = db_path
        self.init_db()

    def connect(self):
        '''
        Create and return a new database connection.
        '''
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        '''
        Initialize the database with the required tables.
        If any required table is missing, clear database and create all tables.
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

        # If any table is missing, clear DB and create all tables
        if not required_tables.issubset(existing_tables):
            self.clear_db()
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
        # Новые числовые статусы (10-19) не изменяются при single_checkbox
        if value >= 10 and value <= 19:
            return value

        # If multi_numbers is enabled and value is not numeric (0, 10-19), map to 0
        if multi_numbers and not (value == 0 or (value >= 10 and value <= 19)):
            return 0

        # If single_checkbox is enabled, map all "done" statuses to 2 ("done")
        if single_checkbox and value in [1, 3]:  # If status is "done mini" or "done elite"
            return 2  # Return "done"

        if fail_by_default:
            # Don't mark future dates as failed
            if value == 0 and current_date and today and current_date >= today:
                return 0

            # Handle dates relative to first tracking
            if value == 0 and first_tracking_date and current_date:
                # Return fail status for dates up to first tracking date
                # Return 0 for dates before first tracking date
                return 9 if current_date > first_tracking_date else 0

            # Default fail_by_default behavior
            if value == 0:
                return 9

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
        start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
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
        first_tracking_date = None
        if fail_by_default:
            first_tracking_date = self.get_first_tracking_date(habit_id_val)
            print(f'first_tracking_date: {first_tracking_date}')

        # Get all records for habit in date range, ordered by date
        cursor.execute('''SELECT date, status
                        FROM habit_tracking
                        WHERE habit_id = ? AND date BETWEEN ? AND ?
                        ORDER BY date''',
                     (habit_id_val, start_date, end_date))

        tracking_rows = cursor.fetchall()
        tracking_dict = {datetime.strptime(row['date'], '%Y-%m-%d').date(): row['status']
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
        :param habit_id: Habit ID or GLOBAL_PARAMS_ID for global parameters
        :param value: Parameter value
        :raises ValueError: If parameter name is invalid for given habit_id
        """
        if habit_id == self.GLOBAL_PARAMS_ID:
            if param_name not in self.VALID_GLOBAL_PARAMS:
                raise ValueError(f"Unknown global parameter: {param_name}")
        else:
            if param_name not in self.VALID_HABIT_PARAMS:
                raise ValueError(f"Unknown habit parameter: {param_name}")

    def get_param(self, habit_id, param_name, default_value=None):
        '''
        Get the value of a specific parameter for a habit or globally.

        :param habit_id: The habit ID (HabitsDatabase.GLOBAL_PARAMS_ID for global parameters).
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

        :param habit_id: The habit ID (HabitsDatabase.GLOBAL_PARAMS_ID for global parameters).
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
                        current_habit_id = -1
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
        Returns list of possible status options for habits
        '''
        return [
            {'value': 0, 'label': 'not set',    'icon': ' ',  'color': 'none', 'neg_color': 'none', 'as_char': ' ', 'image': 'empty.png'},
            {'value': 1, 'label': 'done mini',  'icon': '☑️', 'color': 'green', 'neg_color': 'red', 'as_char': 'v', 'image': 'done_mini.png'},
            {'value': 2, 'label': 'done',       'icon': '✅', 'color': 'green', 'neg_color': 'red', 'as_char': 'V', 'image': 'done.png'},
            {'value': 3, 'label': 'done elite', 'icon': '🌟', 'color': 'gold', 'neg_color': 'red', 'as_char': 'W', 'image': 'done_elite.png'},
            {'value': 9, 'label': 'fail',       'icon': '❌', 'color': 'red', 'neg_color': 'green', 'as_char': 'X', 'image': 'fail.png'},
            {'value': 10, 'label': '0',  'icon': '0️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '0', 'image': 'number_0.png'},
            {'value': 11, 'label': '1',  'icon': '1️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '1', 'image': 'number_1.png'},
            {'value': 12, 'label': '2',  'icon': '2️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '2', 'image': 'number_2.png'},
            {'value': 13, 'label': '3',  'icon': '3️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '3', 'image': 'number_3.png'},
            {'value': 14, 'label': '4',  'icon': '4️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '4', 'image': 'number_4.png'},
            {'value': 15, 'label': '5',  'icon': '5️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '5', 'image': 'number_5.png'},
            {'value': 16, 'label': '6',  'icon': '6️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '6', 'image': 'number_6.png'},
            {'value': 17, 'label': '7',  'icon': '7️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '7', 'image': 'number_7.png'},
            {'value': 18, 'label': '8',  'icon': '8️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '8', 'image': 'number_8.png'},
            {'value': 19, 'label': '9',  'icon': '9️⃣', 'color': 'green', 'neg_color': 'red', 'as_char': '9', 'image': 'number_9.png'},
        ]

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
                return datetime.strptime(row['date'], '%Y-%m-%d').date()
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
