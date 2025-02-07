# habits_core.py
from datetime import datetime, timedelta
from habits_database import HabitsDatabase

# Global variable to hold the Database instance.
database = None

def init_db():
    """
    Initialize the database using the Database object.
    """
    global database
    database = HabitsDatabase()

def api_fetch_habits(args):
    """
    Process query parameters to fetch habits and their tracking data.

    :param args: A dictionary-like object with query parameters (e.g. flask.request.args)
    :return: On success, a dictionary with habit data; on error, a tuple (error dict, status code).
    """
    start_date = args.get('start_date')
    end_date = args.get('end_date')
    habit_id = args.get('habit_id')
    if habit_id:
        try:
            habit_id = int(habit_id)
        except ValueError:
            return {'error': 'Invalid habit_id'}, 400
    if not start_date or not end_date:
        return {'error': 'start_date and end_date parameters are required'}, 400
    try:
        data = database.fetch_habits(start_date, end_date, habit_id)

    except ValueError as e:
        return {'error': str(e)}, 400
    return data

def api_update_habit(json_data):
    """
    Process JSON data to update a habit's tracking status.

    :param json_data: A dictionary with JSON data from the request.
    :return: On success, a dictionary with a confirmation message; on error, a tuple (error dict, status code).
    """
    habit_id = json_data.get('habit_id')
    date = json_data.get('date')
    status = json_data.get('status')
    if habit_id is None or date is None or status is None:
        return {'error': 'habit_id, date, and status are required'}, 400
    try:
        habit_id = int(habit_id)
        status = int(status)
    except ValueError:
        return {'error': 'Invalid habit_id or status value'}, 400

    database.update_habit(habit_id, date, status)

    return {'message': 'Habit status updated successfully'}

def api_add_habit(json_data):
    """
    Process JSON data to add a new habit.

    :param json_data: A dictionary with JSON data from the request.
    :return: On success, a dictionary with a confirmation message and habit_id; on error, a tuple (error dict, status code).
    """
    name = json_data.get('name')
    if not name:
        return {'error': 'Habit name is required'}, 400

    habit_id = database.add_habit(name)

    return {'message': 'Habit added successfully', 'habit_id': habit_id}

def api_delete_habit(json_data):
    """
    Process JSON data to delete a habit and its tracking data.

    :param json_data: A dictionary with JSON data from the request.
    :return: On success, a dictionary with a confirmation message; on error, a tuple (error dict, status code).
    """
    habit_id = json_data.get('habit_id')
    if habit_id is None:
        return {'error': 'habit_id is required'}, 400
    try:
        habit_id = int(habit_id)
    except ValueError:
        return {'error': 'Invalid habit_id'}, 400

    database.delete_habit(habit_id)

    return {'message': 'Habit deleted successfully'}

def api_get_all_habits():
    """
    Retrieve all habits.

    :return: A dictionary containing a list of all habits.
    """
    habits_list = database.get_all_habits()

    return {'habits': habits_list}

def api_export_habits():
    """
    Export all habits data to CSV format.

    :return: CSV data as string
    """
    return '\n'.join(database.export_to_csv())

def api_import_habits(csv_data):
    """
    Import habits from CSV data.

    :param csv_data: CSV data as string
    :return: List of status messages
    """
    database.import_from_csv(csv_data.splitlines())
