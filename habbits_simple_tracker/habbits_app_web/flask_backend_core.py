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
        csv_data = request.get_data(as_text=True)
        messages = api_import_habits(csv_data)
        return jsonify(messages)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
