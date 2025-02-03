# habbits_core.py
import sqlite3
from datetime import datetime, timedelta
from flask import g


def get_db():
    """
    Return a database connection.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """
    Initialize the database with required tables.
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS habits ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'name TEXT NOT NULL)'
    )
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS habit_tracking ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'habit_id INTEGER NOT NULL, '
        'date TEXT NOT NULL, '
        'status INTEGER NOT NULL DEFAULT 0, '
        'UNIQUE(habit_id, date))'
    )
    db.commit()
    db.close()


def fetch_habits(start_date, end_date, habit_id=None):
    """
    Fetch habits and their tracking data within a date range.

    :param start_date: Start date as 'YYYY-MM-DD'.
    :param end_date: End date as 'YYYY-MM-DD'.
    :param habit_id: Optional habit ID; if provided, only this habit is fetched.
    :return: Dictionary with 'start_date', 'end_date', and list of habits with tracking data.
    :raises ValueError: if the date format is invalid.
    """
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Invalid date format. Use YYYY-MM-DD.')

    num_days = (end_dt - start_dt).days + 1
    date_list = [(start_dt + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days)]

    db = get_db()
    cursor = db.cursor()
    if habit_id:
        cursor.execute('SELECT id, name FROM habits WHERE id = ?', (habit_id,))
    else:
        cursor.execute('SELECT id, name FROM habits')
    habits = cursor.fetchall()

    habits_data = []
    for habit in habits:
        habit_id_value = habit['id']
        habit_name = habit['name']
        cursor.execute(
            'SELECT date, status FROM habit_tracking WHERE habit_id = ? AND date BETWEEN ? AND ?',
            (habit_id_value, start_date, end_date)
        )
        tracking_rows = cursor.fetchall()
        tracking_dict = {row['date']: row['status'] for row in tracking_rows}
        tracking = [tracking_dict.get(date, 0) for date in date_list]

        habits_data.append({
            'id': habit_id_value,
            'name': habit_name,
            'tracking': tracking
        })

    return {
        'start_date': start_date,
        'end_date': end_date,
        'habits': habits_data
    }

def update_habit(habit_id, date, status):
    """
    Update the status of a habit on a specific date.

    :param habit_id: ID of the habit.
    :param date: Date as a string in 'YYYY-MM-DD' format.
    :param status: New status as an integer.
    :return: Dictionary with a confirmation message.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        '''
        INSERT INTO habit_tracking (habit_id, date, status)
        VALUES (?, ?, ?)
        ON CONFLICT(habit_id, date) DO UPDATE SET status=excluded.status
        ''',
        (habit_id, date, status)
    )
    db.commit()
    return {'message': 'Habit status updated successfully'}

def add_habit(name):
    """
    Add a new habit.

    :param name: Name of the habit.
    :return: Dictionary with a confirmation message and the habit ID.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO habits (name) VALUES (?)', (name,))
    db.commit()
    habit_id = cursor.lastrowid
    return {'message': 'Habit added successfully', 'habit_id': habit_id}

def delete_habit(habit_id):
    """
    Delete a habit and its associated tracking data.

    :param habit_id: ID of the habit to delete.
    :return: Dictionary with a confirmation message.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM habit_tracking WHERE habit_id = ?', (habit_id,))
    cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
    db.commit()
    return {'message': 'Habit deleted successfully'}

def get_all_habits():
    """
    Get a list of all habits.

    :return: Dictionary containing a list of habits.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name FROM habits')
    habits = cursor.fetchall()
    habits_list = [{'id': habit['id'], 'name': habit['name']} for habit in habits]
    return {'habits': habits_list}
