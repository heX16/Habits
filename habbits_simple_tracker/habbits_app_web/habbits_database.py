import sqlite3
from datetime import datetime, timedelta
import csv

class Database:
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
        '''
        self.create_tables()

    def create_tables(self):
        '''
        Create all necessary tables in the database.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        try:
            conn.execute('BEGIN TRANSACTION')
            
            cursor.execute('CREATE TABLE IF NOT EXISTS habits ('
                          'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                          'name TEXT NOT NULL)')
            
            cursor.execute('CREATE TABLE IF NOT EXISTS habit_tracking ('
                          'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                          'habit_id INTEGER NOT NULL, '
                          'date TEXT NOT NULL, '
                          'status INTEGER NOT NULL DEFAULT 0, '
                          'UNIQUE(habit_id, date))')
            
            cursor.execute('CREATE TABLE IF NOT EXISTS habit_params ('
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
            cursor.execute('DROP TABLE IF EXISTS habits')
            
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
        cursor.execute('INSERT INTO habits (name) VALUES (?)', (name,))
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
        cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
        conn.commit()
        conn.close()

    def update_habit(self, habit_id, date, status):
        '''
        Update the status of a habit for a given date.

        :param habit_id: The ID of the habit.
        :param date: The date in 'YYYY-MM-DD' format.
        :param status: The new status value.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO habit_tracking (habit_id, date, status)
                          VALUES (?, ?, ?)
                          ON CONFLICT(habit_id, date) DO UPDATE SET status=excluded.status''',
                       (habit_id, date, status))
        conn.commit()
        conn.close()

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
        if habit_id:
            cursor.execute('SELECT id, name FROM habits WHERE id = ?', (habit_id,))
        else:
            cursor.execute('SELECT id, name FROM habits')
        habits = cursor.fetchall()
        habits_data = []
        for habit in habits:
            habit_id_val = habit['id']
            habit_name = habit['name']
            cursor.execute('SELECT date, status FROM habit_tracking WHERE habit_id = ? AND date BETWEEN ? AND ?',
                           (habit_id_val, start_date, end_date))
            tracking_rows = cursor.fetchall()
            tracking_dict = {row['date']: row['status'] for row in tracking_rows}
            tracking = [tracking_dict.get(date, 0) for date in date_list]
            habits_data.append({
                'id': habit_id_val,
                'name': habit_name,
                'tracking': tracking
            })
        conn.close()
        return {
            'start_date': start_date,
            'end_date': end_date,
            'habits': habits_data
        }

    def get_all_habits(self):
        '''
        Retrieve a list of all habits.

        :return: A list of dictionaries, each containing the habit ID and name.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM habits')
        habits = cursor.fetchall()
        habits_list = [{'id': habit['id'], 'name': habit['name']} for habit in habits]
        conn.close()
        return habits_list

    def get_param(self, habit_id, param_name):
        '''
        Get the value of a specific parameter for a habit or globally.

        :param habit_id: The habit ID (-1 for global parameters).
        :param param_name: The name of the parameter.
        :return: The value of the parameter, or None if not found.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM habit_params WHERE habit_id = ? AND param_name = ?',
                       (habit_id, param_name))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else None

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
        
        :yield: Each line of CSV data as a string
        '''
        conn = self.connect()
        cursor = conn.cursor()
        
        # Export habits and their tracking data
        cursor.execute('SELECT id, name FROM habits')
        habits = cursor.fetchall()
        for habit in habits:
            yield f'habit:,{habit["name"]}'
            
            # Export tracking data for this habit
            cursor.execute('SELECT date, status FROM habit_tracking WHERE habit_id = ? ORDER BY date', 
                          (habit['id'],))
            tracking = cursor.fetchall()
            for track in tracking:
                yield f'{track["date"]},{track["status"]}'
            
            # Add empty line between habits
            yield ''
        
        # Export global parameters
        cursor.execute('SELECT param_name, value FROM habit_params WHERE habit_id = -1')
        global_params = cursor.fetchall()
        if global_params:  # If there are any global params
            yield 'habit_params:,global'
            for param in global_params:
                yield f'{param["param_name"]},{param["value"]}'
            yield ''
        
        # Export habit-specific parameters
        for habit in habits:
            cursor.execute('SELECT param_name, value FROM habit_params WHERE habit_id = ?', 
                          (habit['id'],))
            params = cursor.fetchall()
            if params:  # Only output section if habit has params
                yield f'habit_params:,{habit["name"]}'
                for param in params:
                    yield f'{param["param_name"]},{param["value"]}'
                yield ''
        
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
            current_habit_name = None
            mode = None  # Can be 'habit' or 'params'
            
            for line in csv_lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                # Split CSV line manually to handle quoted values
                row = next(csv.reader([line]))
                
                if line.startswith('habit:'):
                    # New habit section
                    _, habit_name = row
                    cursor.execute('INSERT INTO habits (name) VALUES (?)', (habit_name,))
                    current_habit_id = cursor.lastrowid
                    current_habit_name = habit_name
                    mode = 'habit'
                    
                elif line.startswith('habit_params:'):
                    # New parameters section
                    _, target = row
                    mode = 'params'
                    if target == 'global':
                        current_habit_id = -1
                    else:
                        # Find habit ID by name
                        cursor.execute('SELECT id FROM habits WHERE name = ?', (target,))
                        result = cursor.fetchone()
                        if result:
                            current_habit_id = result['id']
                        else:
                            mode = None
                    
                elif mode == 'habit':
                    # Tracking data line
                    date, status = row
                    cursor.execute('''INSERT INTO habit_tracking (habit_id, date, status) 
                                    VALUES (?, ?, ?)''', 
                                 (current_habit_id, date, int(status)))
                    
                elif mode == 'params':
                    # Parameter line
                    param_name, value = row
                    cursor.execute('''INSERT INTO habit_params (habit_id, param_name, value) 
                                    VALUES (?, ?, ?)''', 
                                 (current_habit_id, param_name, value))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f'Error during import: {str(e)}')
        
        finally:
            conn.close()

    def get_status_options(self):
        '''
        Get list of possible status values with their descriptions and icons.
        
        :return: List of dictionaries with status options
        '''
        return [
            {'value': 0, 'label': 'empty', 'icon': ''},
            {'value': 1, 'label': 'done', 'icon': '✅'},
            {'value': 2, 'label': 'fail', 'icon': '❌'},
            {'value': 3, 'label': 'done. mini', 'icon': '☑️'},
            {'value': 4, 'label': 'done. elite', 'icon': '🌟'}
        ]
