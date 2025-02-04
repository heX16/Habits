import sqlite3
from datetime import datetime, timedelta
import calendar

class Database:
    '''
    Database class for managing habits and habit tracking.
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
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS habits ('
                       'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                       'name TEXT NOT NULL)')
        cursor.execute('CREATE TABLE IF NOT EXISTS habit_tracking ('
                       'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                       'habit_id INTEGER NOT NULL, '
                       'date TEXT NOT NULL, '
                       'status INTEGER NOT NULL DEFAULT 0, '
                       'UNIQUE(habit_id, date))')
        conn.commit()
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
        Delete a habit and its associated tracking data.

        :param habit_id: The ID of the habit to delete.
        '''
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM habit_tracking WHERE habit_id = ?', (habit_id,))
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
