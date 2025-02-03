# flask_backend_core.py
from flask import Flask, jsonify, request, render_template, g
from habbits_core import init_db, fetch_habits, update_habit, add_habit, delete_habit, get_all_habits

def create_app():
    """
    Create and configure the Flask application with route definitions.

    :return: A Flask application instance.
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Initialize the database on app startup.
    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def close_connection(exception):
        """
        Close the database connection after each request.
        """
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

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
        API endpoint to retrieve habits and tracking data within a date range.
        """
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date parameters are required'}), 400
        try:
            data = fetch_habits(start_date, end_date)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        return jsonify(data)

    @app.route('/api/habits/update', methods=['POST'])
    def api_update_habit():
        """
        API endpoint to update a habit's status.
        """
        data = request.get_json()
        habit_id = data.get('habit_id')
        date = data.get('date')
        status = data.get('status')
        if habit_id is None or date is None or status is None:
            return jsonify({'error': 'habit_id, date, and status are required'}), 400
        result = update_habit(habit_id, date, status)
        return jsonify(result)

    @app.route('/api/habits/add', methods=['POST'])
    def api_add_habit():
        """
        API endpoint to add a new habit.
        """
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({'error': 'Habit name is required'}), 400
        result = add_habit(name)
        return jsonify(result)

    @app.route('/api/habits/delete', methods=['DELETE'])
    def api_delete_habit():
        """
        API endpoint to delete a habit.
        """
        data = request.get_json()
        habit_id = data.get('habit_id')
        if habit_id is None:
            return jsonify({'error': 'habit_id is required'}), 400
        result = delete_habit(habit_id)
        return jsonify(result)

    @app.route('/api/habits/all', methods=['GET'])
    def api_get_all_habits():
        """
        API endpoint to get all habits.
        """
        result = get_all_habits()
        return jsonify(result)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
