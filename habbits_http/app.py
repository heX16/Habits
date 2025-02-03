import sqlite3
from flask import Flask, request, jsonify, render_template, g
from datetime import datetime, timedelta

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    """Return a database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize the database with required tables."""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS habit_tracking (id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER NOT NULL, date TEXT NOT NULL, status INTEGER NOT NULL DEFAULT 0, UNIQUE(habit_id, date))')
    db.commit()
    db.close()

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection after each request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/edit')
def edit():
    """Render the habit editing page."""
    return render_template('edit.html')

@app.route('/api/habits', methods=['GET'])
def get_habits():
    """
    Get habits and their tracking data within a date range.

    Query Parameters:
      - start_date: Starting date in 'YYYY-MM-DD' format.
      - end_date: Ending date in 'YYYY-MM-DD' format.

    Returns:
      A JSON object with the habits and their tracking statuses.
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date parameters are required'}), 400

    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    # Generate list of dates between start_date and end_date (inclusive)
    num_days = (end_dt - start_dt).days + 1
    date_list = [(start_dt + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days)]

    db = get_db()
    cursor = db.cursor()
    # Get all habits
    cursor.execute('SELECT id, name FROM habits')
    habits = cursor.fetchall()

    habits_data = []
    for habit in habits:
        habit_id = habit['id']
        habit_name = habit['name']
        # Get tracking data for the habit within the date range
        cursor.execute('SELECT date, status FROM habit_tracking WHERE habit_id = ? AND date BETWEEN ? AND ?', (habit_id, start_date, end_date))
        tracking_rows = cursor.fetchall()
        # Create a mapping from date to status
        tracking_dict = {row['date']: row['status'] for row in tracking_rows}
        # Build tracking array for each date in date_list; default status is 0
        tracking = [tracking_dict.get(date, 0) for date in date_list]

        habits_data.append({
            'id': habit_id,
            'name': habit_name,
            'tracking': tracking
        })

    response = {
        'start_date': start_date,
        'end_date': end_date,
        'habits': habits_data
    }
    return jsonify(response)

@app.route('/api/habits/update', methods=['POST'])
def update_habit():
    """
    Update the status of a habit on a specific date.

    Request JSON:
      {
        "habit_id": int,
        "date": "YYYY-MM-DD",
        "status": int
      }

    Returns:
      A JSON object confirming the update.
    """
    data = request.get_json()
    habit_id = data.get('habit_id')
    date = data.get('date')
    status = data.get('status')

    if habit_id is None or date is None or status is None:
        return jsonify({'error': 'habit_id, date, and status are required'}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        # Insert or update the tracking record using SQLite UPSERT
        cursor.execute('''
            INSERT INTO habit_tracking (habit_id, date, status)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, date) DO UPDATE SET status=excluded.status
        ''', (habit_id, date, status))
        db.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Habit status updated successfully'})

@app.route('/api/habits/add', methods=['POST'])
def add_habit():
    """
    Add a new habit.

    Request JSON:
      {
        "name": "Habit Name"
      }

    Returns:
      A JSON object confirming the addition.
    """
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Habit name is required'}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO habits (name) VALUES (?)', (name,))
        db.commit()
        habit_id = cursor.lastrowid
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Habit added successfully', 'habit_id': habit_id})

@app.route('/api/habits/delete', methods=['DELETE'])
def delete_habit():
    """
    Delete a habit and its associated tracking data.

    Request JSON:
      {
        "habit_id": int
      }

    Returns:
      A JSON object confirming the deletion.
    """
    data = request.get_json()
    habit_id = data.get('habit_id')

    if habit_id is None:
        return jsonify({'error': 'habit_id is required'}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        # Delete tracking data first
        cursor.execute('DELETE FROM habit_tracking WHERE habit_id = ?', (habit_id,))
        # Delete the habit
        cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
        db.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Habit deleted successfully'})

@app.route('/api/habits/all', methods=['GET'])
def get_all_habits():
    """
    Get all habits without tracking data.

    Returns:
      A JSON object containing a list of habits.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name FROM habits')
    habits = cursor.fetchall()

    habits_list = [{'id': habit['id'], 'name': habit['name']} for habit in habits]
    return jsonify({'habits': habits_list})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
