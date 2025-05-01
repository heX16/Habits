# flask_backend_core.py
"""
URL structure:

Pages:
http://server.test/habits/                    - Main page (index.html)
http://server.test/habits/edit               - Edit habits page (edit.html)
http://server.test/habits/backup             - Backup/restore page (backup.html)
http://server.test/habits/options            - Global options page (options.html)
http://server.test/habits/habit/2            - Single habit page (habit.html)
http://server.test/habits/habit/2/options    - Single habit options page (habit_options.html)

API endpoints:
http://server.test/habits/api/habits              - GET: fetch habits data
http://server.test/habits/api/habits/update       - POST: update habit status
http://server.test/habits/api/habits/add          - POST: add new habit
http://server.test/habits/api/habits/delete       - DELETE: delete habit
http://server.test/habits/api/habits/list         - GET: list all habits
http://server.test/habits/api/habits/rename       - POST: rename habit
http://server.test/habits/api/habits/export       - GET: export habits to CSV
http://server.test/habits/api/habits/import       - POST: import habits from CSV
http://server.test/habits/api/param/<name>        - GET/POST: get/set global parameter
http://server.test/habits/api/param/<name>/<id>   - GET/POST: get/set habit parameter
http://server.test/habits/api/main_page          - GET: fetch main page data

Static files:
http://server.test/habits/static/script.js   - Main page script
http://server.test/habits/static/habit.js    - Single habit page script
http://server.test/habits/static/edit.js     - Edit page script
http://server.test/habits/static/menu.js     - Floating menu component
http://server.test/habits/static/style.css   - Styles
http://server.test/habits/js/constants.js    - Generated constants
"""
import os
from flask import Flask, jsonify, request, render_template, send_file, Response, redirect, url_for, send_from_directory
from web.habits_core import init_db, api_fetch_habits, api_fetch_main_page, api_update_habit, api_add_habit, api_delete_habit, api_get_all_habits, api_export_habits, api_import_habits, api_rename_habit, api_reorder_habit, prepare_js_constants, get_database
from common_lib.habits_database import HabitsDatabase

def create_app():
    """
    Create and configure the Flask application with route definitions.
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Get database instance from core
    db = get_database()

    # Initialize the database on app startup.
    with app.app_context():
        init_db(db)

    @app.route('/favicon.ico')
    def favicon():
        """
        Serve the favicon.ico file from the static folder.
        """
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/favicon.png')
    def favicon_png():
        """
        Serve the favicon.png file from the static folder.
        """
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.png', mimetype='image/png')

    @app.route('/')
    def index():
        """
        Render the main habit tracker page.
        """
        return render_template('index.html', options_page_url=url_for('options_page'))

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

    @app.route('/habit/<int:habit_id>/api/habits', methods=['GET'])
    def api_get_habit_data(habit_id):
        """
        API endpoint to retrieve habit data for a specific habit.
        Delegates to the main habits API with the habit_id parameter.
        """
        args = dict(request.args)
        args['habit_id'] = habit_id
        result = api_fetch_habits(args, db)
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

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

        template_data = prepare_js_constants(db)
        js_content = render_template('constants.js', **template_data)

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
        Render the combined options page.
        """
        return render_template('options.html', db_path=db.db_path)

    @app.route('/api/param/<param_name>', methods=['GET'])
    @app.route('/api/param/<param_name>/<int:habit_id>', methods=['GET'])
    def get_param(param_name, habit_id=HabitsDatabase.GLOBAL_PARAMS):
        """
        Get parameter value.
        If habit_id is not provided, returns global parameter (habit_id = GLOBAL_PARAMS)

        :param param_name: Name of the parameter
        :param habit_id: Optional habit ID (default: GLOBAL_PARAMS for global parameters)
        """
        value = db.get_param(habit_id, param_name) or 'false'
        return jsonify({'value': value})

    @app.route('/api/param/<param_name>', methods=['POST'])
    @app.route('/api/param/<param_name>/<int:habit_id>', methods=['POST'])
    def set_param(param_name, habit_id=HabitsDatabase.GLOBAL_PARAMS):
        """
        Set parameter value.
        If habit_id is not provided, sets global parameter (habit_id = GLOBAL_PARAMS)

        :param param_name: Name of the parameter
        :param habit_id: Optional habit ID (default: GLOBAL_PARAMS for global parameters)
        """
        data = request.get_json()
        if 'value' not in data:
            return jsonify({'error': 'value is required'}), 400

        db.set_param(habit_id, param_name, data['value'])
        return jsonify({'message': 'Parameter updated successfully'})

    @app.route('/habit/<int:habit_id>/options')
    def habit_options(habit_id):
        """
        Render the options page for a specific habit.
        """
        return render_template('habit_options.html', habit_id=habit_id)

    @app.route('/api/habits/rename', methods=['POST'])
    def api_rename():
        """
        API endpoint to rename a habit.
        """
        result = api_rename_habit(request.get_json(), db)
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/main_page', methods=['GET'])
    def api_get_main_page():
        """
        API endpoint to retrieve main page data.
        Currently returns the same data as /api/habits endpoint.
        """
        result = api_fetch_main_page(request.args, db)
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    @app.route('/api/habits/reorder', methods=['POST'])
    def api_reorder():
        """
        API endpoint to reorder habits.
        """
        result = api_reorder_habit(request.get_json(), db)
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        return jsonify(result)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
