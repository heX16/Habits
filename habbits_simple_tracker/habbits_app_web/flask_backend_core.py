# flask_backend_core.py
import os
from flask import Flask, jsonify, request, render_template, send_file, Response
from habits_core import init_db, api_fetch_habits, api_update_habit, api_add_habit, api_delete_habit, api_get_all_habits, api_export_habits, api_import_habits
from habits_database import HabitsDatabase

def create_app():
    """
    Create and configure the Flask application with route definitions.
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Get database path from environment variable or use default
    db_path = os.environ.get('HABITS_WEB_DB_PATH', 'habits.db')
    db = HabitsDatabase(db_path)

    # Initialize the database on app startup.
    with app.app_context():
        init_db(db)

    @app.route('/')
    def index():
        """
        Render the main habit tracker page.
        """
        return render_template('index.html')

    @app.route('/edit')
    def edit():
        """
        Render the habit editing page.
        """
        return render_template('edit.html')

    @app.route('/api/habits', methods=['GET'])
    def api_get_habits():
        """
        API endpoint to retrieve habits and their tracking data.
        Delegates argument parsing to habits_core.api_fetch_habits.
        """
        result = api_fetch_habits(request.args, db)
        # If an error is returned as a tuple, unpack the error message and status code.
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/update', methods=['POST'])
    def api_update():
        """
        API endpoint to update a habit's status.
        Delegates JSON parsing to habits_core.api_update_habit.
        """
        result = api_update_habit(request.get_json(), db)
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/add', methods=['POST'])
    def api_add():
        """
        API endpoint to add a new habit.
        """
        result = api_add_habit(request.get_json(), db)
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/delete', methods=['DELETE'])
    def api_delete():
        """
        API endpoint to delete a habit.
        """
        result = api_delete_habit(request.get_json(), db)
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/list', methods=['GET'])
    def api_list():
        """
        API endpoint to list all habits.
        """
        return jsonify(api_get_all_habits(db))

    @app.route('/habit/<int:habit_id>')
    def habit_page(habit_id):
        """
        Render the habit page for a specific habit.
        """
        return render_template('habit.html', habit_id=habit_id)

    @app.route('/backup')
    def backup_page():
        return render_template('backup.html')

    @app.route('/api/habits/export', methods=['GET'])
    def api_export():
        """
        API endpoint to export habits data.
        """
        csv_data = api_export_habits(db)
        return Response(csv_data, mimetype='text/csv')

    @app.route('/api/habits/import', methods=['POST'])
    def api_import():
        """
        API endpoint to import habits data.
        """
        csv_data = request.get_data(as_text=True)
        api_import_habits(csv_data, db)
        return jsonify({'status': 'success'})

    @app.route('/js/constants.js')
    def js_constants():
        """
        Generate JavaScript constants dynamically with caching headers
        """
        cache_duration_sec = 60 * 60 * 1

        constants = {
            'singleClickMaxStatus': 3,
            'tableDaysCount': 10
        }

        status_options = db.get_status_options()
        formatted_options = []
        for option in status_options:
            formatted_items = []
            for k, v in option.items():
                if isinstance(v, str):
                    formatted_items.append(f"'{k}': '{v}'")
                else:
                    formatted_items.append(f"'{k}': {v}")
            formatted_options.append('{' + ', '.join(formatted_items) + '}')
        
        status_options_js_str = ',\n        '.join(formatted_options)

        js_content =  f"// This file is generated automatically\n"
        js_content += f"const {list(constants.keys())[0]} = {list(constants.values())[0]};\n"
        js_content += f"const {list(constants.keys())[1]} = {list(constants.values())[1]};\n"
        js_content += f"\n"
        js_content += f"const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];\n"
        js_content += f"\n"
        js_content += f"function getStatusOptions() {{\n"
        js_content += f"    return [\n"
        js_content += f"        {status_options_js_str}\n"
        js_content += f"    ];\n"
        js_content += f"}}\n"

        response = app.response_class(
            response=js_content,
            status=200,
            mimetype='application/javascript'
        )

        response.headers['Cache-Control'] = f'public, max-age={cache_duration_sec}'
        response.add_etag()

        return response.make_conditional(request)

    @app.route('/options')
    def options_page():
        """
        Render the options page.
        """
        return render_template('options.html', db_path=db.db_path)

    @app.route('/api/param/<param_name>', methods=['GET'])
    @app.route('/api/param/<param_name>/<int:habit_id>', methods=['GET'])
    def get_param(param_name, habit_id=-1):
        """
        Get parameter value.
        If habit_id is not provided, returns global parameter (habit_id = -1)

        :param param_name: Name of the parameter
        :param habit_id: Optional habit ID (default: -1 for global parameters)
        """
        from habits_core import database
        value = database.get_param(habit_id, param_name) or 'false'
        return jsonify({'value': value})

    @app.route('/api/param/<param_name>', methods=['POST'])
    @app.route('/api/param/<param_name>/<int:habit_id>', methods=['POST'])
    def set_param(param_name, habit_id=-1):
        """
        Set parameter value.
        If habit_id is not provided, sets global parameter (habit_id = -1)

        :param param_name: Name of the parameter
        :param habit_id: Optional habit ID (default: -1 for global parameters)
        """
        from habits_core import database
        data = request.get_json()
        if 'value' not in data:
            return jsonify({'error': 'value is required'}), 400

        database.set_param(habit_id, param_name, data['value'])
        return jsonify({'message': 'Parameter updated successfully'})

    @app.route('/habit/<int:habit_id>/options')
    def habit_options(habit_id):
        """
        Render the options page for a specific habit.
        """
        return render_template('habit_options.html', habit_id=habit_id)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
