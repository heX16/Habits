import sqlite3
from datetime import datetime, timedelta
import csv

class HabitsDatabase:
    '''
    Database class for managing habits, habit tracking, and special parameters.
    '''
    def __init__(self, db_name='database.db'):
        '''
        Initialize the Database object and create tables if they do not exist.
        '''
        self.db_name = db_name
        self.init_db()

    def connect(self):
        '''
        Create and return a new database connection.
        '''
        conn = sqlite3.connect(self.db_name)
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
                         'name TEXT NOT NULL)')
            
            cursor.execute('CREATE TABLE habit_tracking ('
                         'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                         'habit_id INTEGER NOT NULL, '
                         'date TEXT NOT NULL, '
                         'status INTEGER NOT NULL DEFAULT 0, '
                         'UNIQUE(habit_id, date))')
            
            cursor.execute('CREATE TABLE habit_params ('
                         'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                         'habit_id INTEGER NOT NULL, '  # -1 for global/user-level params
                         'param_name TEXT NOT NULL, '
                         'value TEXT NOT NULL, '
                         'UNIQUE(habit_id, param_name))')
            
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
        cursor.execute('INSERT INTO habits_list (name) VALUES (?)', (name,))
        conn.commit()
        habit_id = cursor.lastrowid
        conn.close()
        return habit_id

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

    def status_mapping(self, value: int, habit_id: int, fail_by_default: bool = False) -> int:
        '''
        Maps database status values to client-side values.
        Takes into account habit's fail_by_default parameter.

        :param value: The status value from database
        :param habit_id: The ID of the habit
        :param fail_by_default: The fail_by_default parameter value ('0' or '1')
        :return: Mapped status value for client
        '''
        if value == 0:
            return 9 if fail_by_default else 0
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
            cursor.execute('SELECT id, name FROM habits_list WHERE id = ?', (habit_id,))
            habits = cursor.fetchall()
            if not habits:
                conn.close()
                raise Exception(f'Habit with id {habit_id} not found')
        else:
            cursor.execute('SELECT id, name FROM habits_list')
            habits = cursor.fetchall()
            
        habits_list = [{'id': habit['id'], 'name': habit['name']} for habit in habits]
        conn.close()
        return habits_list

    def fetch_habit(self, habit, start_date, end_date, cursor):
        '''
        Fetch tracking data for a single habit.
        
        :param habit: Dictionary containing habit info (id and name) or habit ID
        :param start_date: The start date as 'YYYY-MM-DD'
        :param end_date: The end date as 'YYYY-MM-DD'
        :param cursor: Database cursor
        :return: Dictionary with habit data and tracking
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
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        num_days = (end_dt - start_dt).days + 1
        date_list = [(start_dt + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days)]
        
        # Get fail_by_default parameter for this habit
        fail_by_default: bool = self.get_param(habit_id_val, 'fail_by_default', '0') == '1'
        
        # Get all records for habit in date range, ordered by date
        cursor.execute('''SELECT date, status 
                        FROM habit_tracking 
                        WHERE habit_id = ? AND date BETWEEN ? AND ?
                        ORDER BY date''',
                     (habit_id_val, start_date, end_date))
                     
        tracking_rows = cursor.fetchall()
        tracking_dict = {row['date']: row['status'] for row in tracking_rows}
        
        tracking = []
        for date in date_list:
            status = tracking_dict.get(date, 0)
            status = self.status_mapping(status, habit_id_val, fail_by_default=fail_by_default)
            tracking.append(status)
        
        return {
            'id': habit_id_val,
            'name': habit_name,
            'tracking': tracking
        }

    def fetch_habits(self, start_date, end_date, habit_id=None):
        '''
        Fetch habits and their tracking data within a specified date range.
        
        :param start_date: The start date as 'YYYY-MM-DD'.
        :param end_date: The end date as 'YYYY-MM-DD'.
        :param habit_id: Optional habit ID to fetch a specific habit.
        :return: A dictionary containing the start_date, end_date, and a list of habits with tracking data.
        :raises ValueError: If the date format is invalid.
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
                habit_data = self.fetch_habit(habit, start_date, end_date, cursor)
                if habit_data:
                    habits_data.append(habit_data)
                
        finally:
            conn.close()
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'habits': habits_data
        }

    def get_param(self, habit_id, param_name, default_value=None):
        '''
        Get the value of a specific parameter for a habit or globally.

        :param habit_id: The habit ID (-1 for global parameters).
        :param param_name: The name of the parameter.
        :param default_value: Value to return if parameter is not found.
        :return: The value of the parameter, or default_value if not found.
        '''
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

        :param habit_id: The habit ID (-1 for global parameters).
        :param param_name: The name of the parameter.
        :param value: The value to store.
        '''
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
                yield f'habit:,{habit["name"]}'
                
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
                    _, habit_name = row
                    current_habit_id = self.add_habit(habit_name)
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
            {'value': 0, 'label': 'not set', 'icon': '', 'color': 'none', 'as_char': ' '},
            {'value': 1, 'label': 'done mini', 'icon': '☑️', 'color': 'green', 'as_char': 'v'},
            {'value': 2, 'label': 'done', 'icon': '✅', 'color': 'green', 'as_char': 'V'},
            {'value': 3, 'label': 'done elite', 'icon': '🌟', 'color': 'gold', 'as_char': 'W'},
            {'value': 9, 'label': 'fail', 'icon': '❌', 'color': 'red', 'as_char': 'X'}
        ]
