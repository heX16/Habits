# habits_core.py
from datetime import datetime, timedelta
from habits_database import HabitsDatabase

def init_db(database):
    """
    Initialize the database.
    """
    database.init_db()

def api_fetch_habits(args, database):
    """
    Fetch habits data based on request arguments.
    """
    start_date = args.get('start_date')
    end_date = args.get('end_date')
    habit_id = args.get('habit_id')
    
    if habit_id:
        habit_id = int(habit_id)
    
    if not start_date or not end_date:
        return {'error': 'Missing required parameters'}, 400
        
    try:
        return database.fetch_habits(start_date, end_date, habit_id)
    except ValueError as e:
        return {'error': str(e)}, 400

def api_update_habit(data, database):
    """
    Update habit status based on request data.
    """
    if not all(k in data for k in ('habit_id', 'date', 'status')):
        return {'error': 'Missing required fields'}, 400
        
    try:
        database.update_habit(data['habit_id'], data['date'], data['status'])
        return {'status': 'success'}
    except Exception as e:
        return {'error': str(e)}, 500

def api_add_habit(json_data, database):
    """
    Process JSON data to add a new habit.

    :param json_data: A dictionary with JSON data from the request.
    :param database: Database instance
    :return: On success, a dictionary with a confirmation message and habit_id; on error, a tuple (error dict, status code).
    """
    name = json_data.get('name')
    if not name:
        return {'error': 'Habit name is required'}, 400

    habit_id = database.add_habit(name)
    return {'message': 'Habit added successfully', 'habit_id': habit_id}

def api_delete_habit(json_data, database):
    """
    Process JSON data to delete a habit and its tracking data.

    :param json_data: A dictionary with JSON data from the request.
    :param database: Database instance
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

def api_get_all_habits(database):
    """
    Retrieve all habits.

    :param database: Database instance
    :return: A dictionary containing a list of all habits.
    """
    habits_list = database.get_habits_list()
    return {'habits': habits_list}

def api_export_habits(database):
    """
    Export all habits data to CSV format.

    :param database: Database instance
    :return: CSV data as string
    """
    return '\n'.join(database.export_to_csv())

def api_import_habits(csv_data, database):
    """
    Import habits from CSV data.

    :param csv_data: CSV data as string
    :param database: Database instance
    :return: List of status messages
    """
    database.import_from_csv(csv_data.splitlines())

def api_rename_habit(json_data, database):
    """
    Process JSON data to rename a habit.

    :param json_data: A dictionary with JSON data from the request
    :param database: Database instance
    :return: On success, a dictionary with a confirmation message; on error, a tuple (error dict, status code)
    """
    habit_id = json_data.get('habit_id')
    new_name = json_data.get('new_name')
    
    if habit_id is None or new_name is None:
        return {'error': 'habit_id and new_name are required'}, 400
        
    try:
        habit_id = int(habit_id)
    except ValueError:
        return {'error': 'Invalid habit_id'}, 400
        
    if not new_name.strip():
        return {'error': 'New name cannot be empty'}, 400
        
    try:
        database.rename_habit(habit_id, new_name)
        return {'message': 'Habit renamed successfully'}
    except Exception as e:
        return {'error': str(e)}, 400

def prepare_js_constants(database):
    """
    Prepare data for JavaScript constants template.
    
    :param database: Database instance
    :return: Dictionary with template variables
    """
    habits_list = database.get_habits_list()
    
    constants = {
        'singleClickMaxStatus': 3,
        'tableDaysCount': 10,
        'approximateHabitsCount': len(habits_list)
    }

    status_options = database.get_status_options()
    formatted_options = []
    for option in status_options:
        formatted_items = []
        for k, v in option.items():
            if isinstance(v, str):
                formatted_items.append(f"'{k}': '{v}'")
            else:
                formatted_items.append(f"'{k}': {v}")
        formatted_options.append('{' + ', '.join(formatted_items) + '}')

    return {
        'constants': constants,
        'status_options': formatted_options
    }
