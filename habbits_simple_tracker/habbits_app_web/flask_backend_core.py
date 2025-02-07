# flask_backend_core.py
from flask import Flask, jsonify, request, render_template, send_file
from habbits_core import init_db, api_fetch_habits, api_update_habit, api_add_habit, api_delete_habit, api_get_all_habits, api_export_habits, api_import_habits

def create_app():
    """
    Create and configure the Flask application with route definitions.
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Initialize the database on app startup.
    with app.app_context():
        init_db()

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
        Delegates argument parsing to habbits_core.api_fetch_habits.
        """
        result = api_fetch_habits(request.args)
        # If an error is returned as a tuple, unpack the error message and status code.
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/update', methods=['POST'])
    def api_update():
        """
        API endpoint to update a habit's status.
        Delegates JSON parsing to habbits_core.api_update_habit.
        """
        result = api_update_habit(request.get_json())
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/add', methods=['POST'])
    def api_add():
        """
        API endpoint to add a new habit.
        Delegates JSON parsing to habbits_core.api_add_habit.
        """
        result = api_add_habit(request.get_json())
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/delete', methods=['DELETE'])
    def api_delete():
        """
        API endpoint to delete a habit.
        Delegates JSON parsing to habbits_core.api_delete_habit.
        """
        result = api_delete_habit(request.get_json())
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/all', methods=['GET'])
    def api_all():
        """
        API endpoint to retrieve all habits.
        """
        result = api_get_all_habits()
        return jsonify(result)

    @app.route('/stat/<int:habit_id>')
    def stat_page(habit_id):
        """
        Render the statistics page for a specific habit.
        """
        return render_template('stat.html', habit_id=habit_id)

    @app.route('/backup')
    def backup_page():
        return render_template('backup.html')

    @app.route('/api/habits/export')
    def export_habits():
        return api_export_habits()

    @app.route('/api/habits/import', methods=['POST'])
    def import_habits():
        try:
            csv_data = request.get_data(as_text=True)
            if not csv_data:
                return jsonify({'error': 'No data received'}), 400
            
            api_import_habits(csv_data)
            return jsonify({'message': 'Import completed successfully'})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/js/constants.js')
    def js_constants():
        """
        Generate JavaScript constants dynamically with caching headers
        """
        from habbits_core import database
        
        cache_duration_sec = 60 * 60 * 1
        
        constants = {
            'singleClickMaxStatus': 3,
            'tableDaysCount': 10
        }
        
        status_options = database.get_status_options()
        status_options_js = ',\n        '.join(
            f"{{value: {opt['value']}, label: '{opt['label']}', icon: '{opt['icon']}'}}"
            for opt in status_options
        )
        
        js_content =  f"// This file is generated automatically\n"
        js_content += f"const {list(constants.keys())[0]} = {list(constants.values())[0]};\n"
        js_content += f"const {list(constants.keys())[1]} = {list(constants.values())[1]};\n"
        js_content += f"\n"
        js_content += f"const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];\n"
        js_content += f"\n"
        js_content += f"function getStatusOptions() {{\n"
        js_content += f"    return [\n"
        js_content += f"        {status_options_js}\n" 
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
        return render_template('options.html')

    @app.route('/api/param/<param_name>', methods=['GET'])
    @app.route('/api/param/<param_name>/<int:habit_id>', methods=['GET'])
    def get_param(param_name, habit_id=-1):
        """
        Get parameter value.
        If habit_id is not provided, returns global parameter (habit_id = -1)

        :param param_name: Name of the parameter
        :param habit_id: Optional habit ID (default: -1 for global parameters)
        """
        from habbits_core import database
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
        from habbits_core import database
        data = request.get_json()
        if 'value' not in data:
            return jsonify({'error': 'value is required'}), 400
        
        database.set_param(habit_id, param_name, data['value'])
        return jsonify({'message': 'Parameter updated successfully'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
