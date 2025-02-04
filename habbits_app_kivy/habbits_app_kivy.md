Below is one example of how you might implement an analogous Android habit‐tracker application in Python using the [Kivy](https://kivy.org/) framework. In this example the application uses SQLite (as in the original code) to store habits and their tracking data and provides three screens:

1. **Tracker Screen** – displays a table (for the last 7 days) with one row per habit. Tapping a cell cycles the status (0 → 1 → 2 → 0). A “Stats” button per habit switches to the statistics view.
2. **Edit Screen** – lets the user add new habits and delete existing ones.
3. **Statistics Screen** – shows a statistics table for a selected habit (two rows: one for the previous month and one for the current month).

The code is organized in two files. All program code comments and documentation strings are in English.

---

### File: `database.py`

```python
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
```

---

### File: `main.py`

```python
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.properties import NumericProperty
from datetime import datetime, timedelta
import calendar
from database import Database

# Initialize the database
db = Database()

class TrackerScreen(Screen):
    '''
    Screen for displaying the habit tracker table.
    '''
    def on_enter(self):
        '''
        Refresh the tracker table when the screen is entered.
        '''
        self.refresh_table()

    def refresh_table(self):
        '''
        Build and display the habit tracker table with habits and their statuses.
        '''
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical')

        # Navigation bar with button to switch to the Edit screen
        nav_bar = BoxLayout(size_hint_y=0.1)
        btn_edit = Button(text='Edit Habits')
        btn_edit.bind(on_release=lambda x: self.manager.current='edit')
        nav_bar.add_widget(btn_edit)
        layout.add_widget(nav_bar)

        # Calculate the date range for the last 7 days (including today)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=6)
        date_list = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

        # Create header row for the table
        table = GridLayout(cols=2+len(date_list), size_hint_y=None)
        table.bind(minimum_height=table.setter('height'))
        table.add_widget(Label(text='Habit', size_hint_y=None, height=40))
        for date in date_list:
            table.add_widget(Label(text=date, size_hint_y=None, height=40))
        table.add_widget(Label(text='Stats', size_hint_y=None, height=40))

        # Retrieve all habits and build a row for each
        habits = db.get_all_habits()
        for habit in habits:
            habit_id = habit['id']
            habit_name = habit['name']
            table.add_widget(Label(text=habit_name, size_hint_y=None, height=40))

            # Fetch tracking data for this habit over the date range
            data = db.fetch_habits(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), habit_id)
            tracking = data['habits'][0]['tracking'] if data['habits'] else [0]*7

            # Create a button for each day that cycles the habit status when pressed
            for i, status in enumerate(tracking):
                btn = Button(text=self.get_status_text(status), size_hint_y=None, height=40)
                btn.habit_id = habit_id
                btn.date = date_list[i]
                btn.status = status
                btn.bind(on_release=self.cycle_status)
                table.add_widget(btn)

            # Add a Stats button for this habit to view detailed statistics
            btn_stats = Button(text='Stats', size_hint_y=None, height=40)
            btn_stats.habit_id = habit_id
            btn_stats.bind(on_release=self.show_stats)
            table.add_widget(btn_stats)

        scroll = ScrollView()
        scroll.add_widget(table)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def cycle_status(self, instance):
        '''
        Cycle the status of a habit (0 -> 1 -> 2 -> 0) and update the database.

        :param instance: The button instance representing a cell in the tracker table.
        '''
        new_status = (instance.status + 1) % 3
        instance.status = new_status
        instance.text = self.get_status_text(new_status)
        db.update_habit(instance.habit_id, instance.date, new_status)

    def get_status_text(self, status):
        '''
        Return an emoji representing the habit status.

        :param status: The status code.
        :return: An emoji string corresponding to the status.
        '''
        if status == 0:
            return ''
        elif status == 1:
            return '✅'
        elif status == 2:
            return '❌'
        return ''

    def show_stats(self, instance):
        '''
        Switch to the statistics screen for the selected habit.

        :param instance: The Stats button instance.
        '''
        stat_screen = self.manager.get_screen('stat')
        stat_screen.habit_id = instance.habit_id
        self.manager.current = 'stat'

class EditScreen(Screen):
    '''
    Screen for editing habits: adding new habits and deleting existing ones.
    '''
    def on_enter(self):
        '''
        Refresh the list of habits when the screen is entered.
        '''
        self.refresh_list()

    def refresh_list(self):
        '''
        Build and display the list of habits with options to add or delete habits.
        '''
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical')

        # Navigation bar with button to go back to the Tracker screen
        nav_bar = BoxLayout(size_hint_y=0.1)
        btn_tracker = Button(text='Back to Tracker')
        btn_tracker.bind(on_release=lambda x: self.manager.current='tracker')
        nav_bar.add_widget(btn_tracker)
        layout.add_widget(nav_bar)

        # Section for adding a new habit
        add_layout = BoxLayout(size_hint_y=0.1)
        self.habit_input = TextInput(hint_text='Enter habit name')
        btn_add = Button(text='Add Habit')
        btn_add.bind(on_release=self.add_habit)
        add_layout.add_widget(self.habit_input)
        add_layout.add_widget(btn_add)
        layout.add_widget(add_layout)

        # List existing habits with a delete button for each
        scroll = ScrollView()
        habit_list_layout = GridLayout(cols=2, size_hint_y=None)
        habit_list_layout.bind(minimum_height=habit_list_layout.setter('height'))
        habits = db.get_all_habits()
        for habit in habits:
            lbl = Label(text=habit['name'], size_hint_y=None, height=40)
            btn_delete = Button(text='Delete', size_hint_y=None, height=40)
            btn_delete.habit_id = habit['id']
            btn_delete.bind(on_release=self.delete_habit)
            habit_list_layout.add_widget(lbl)
            habit_list_layout.add_widget(btn_delete)
        scroll.add_widget(habit_list_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def add_habit(self, instance):
        '''
        Add a new habit to the database.

        :param instance: The Add Habit button instance.
        '''
        name = self.habit_input.text.strip()
        if name:
            db.add_habit(name)
            self.habit_input.text = ''
            self.refresh_list()

    def delete_habit(self, instance):
        '''
        Delete a habit from the database.

        :param instance: The Delete button instance.
        '''
        db.delete_habit(instance.habit_id)
        self.refresh_list()

class StatScreen(Screen):
    '''
    Screen for displaying detailed statistics for a specific habit.
    '''
    habit_id = NumericProperty(0)

    def on_enter(self):
        '''
        Refresh the statistics view when the screen is entered.
        '''
        self.refresh_stats()

    def refresh_stats(self):
        '''
        Build and display a statistics table for the selected habit.
        The table shows two rows: Previous Month and Current Month.
        '''
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical')

        # Navigation bar with button to go back to the Tracker screen
        nav_bar = BoxLayout(size_hint_y=0.1)
        btn_tracker = Button(text='Back to Tracker')
        btn_tracker.bind(on_release=lambda x: self.manager.current='tracker')
        nav_bar.add_widget(btn_tracker)
        layout.add_widget(nav_bar)

        # Calculate boundaries for previous month and current month
        now = datetime.today()
        current_year = now.year
        current_month = now.month
        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year
        prev_month_start = datetime(prev_year, prev_month, 1)
        next_month = datetime(current_year, current_month + 1, 1) if current_month < 12 else datetime(current_year + 1, 1, 1)
        current_month_end = next_month - timedelta(days=1)
        start_date = prev_month_start.strftime('%Y-%m-%d')
        end_date = current_month_end.strftime('%Y-%m-%d')

        # Fetch tracking data for the habit over the calculated date range
        data = db.fetch_habits(start_date, end_date, self.habit_id)
        if data['habits']:
            tracking = data['habits'][0]['tracking']
        else:
            tracking = []

        # Calculate number of days in previous and current months
        days_in_prev = calendar.monthrange(prev_year, prev_month)[1]
        days_in_current = calendar.monthrange(current_year, current_month)[1]

        # Create a table with two rows (Previous Month and Current Month) and 31 columns
        table = GridLayout(cols=32, size_hint_y=None)
        table.bind(minimum_height=table.setter('height'))

        # Header row with day numbers 1 to 31
        table.add_widget(Label(text=''))
        for i in range(1, 32):
            table.add_widget(Label(text=str(i)))

        # Previous Month row
        table.add_widget(Label(text='Previous Month'))
        for i in range(1, 32):
            btn = Button(text='', size_hint_y=None, height=30)
            if i <= days_in_prev:
                status = tracking[i-1] if len(tracking) >= i else 0
                btn.background_color = self.get_status_color(status)
            table.add_widget(btn)

        # Current Month row
        table.add_widget(Label(text='Current Month'))
        for i in range(1, 32):
            btn = Button(text='', size_hint_y=None, height=30)
            if i <= days_in_current:
                index = days_in_prev + i - 1
                status = tracking[index] if len(tracking) > index else 0
                btn.background_color = self.get_status_color(status)
            table.add_widget(btn)

        scroll = ScrollView()
        scroll.add_widget(table)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def get_status_color(self, status):
        '''
        Return a background color based on the status.

        :param status: The status code.
        :return: A list representing the RGBA color.
        '''
        if status == 1:
            return [0.5, 1, 0.5, 1]  # light green
        elif status == 2:
            return [1, 0.5, 0.5, 1]  # light coral
        else:
            return [1, 1, 1, 1]  # white

class HabitTrackerApp(App):
    '''
    Main application class for the Habit Tracker.
    '''
    def build(self):
        '''
        Build and return the root widget.
        '''
        sm = ScreenManager()
        sm.add_widget(TrackerScreen(name='tracker'))
        sm.add_widget(EditScreen(name='edit'))
        sm.add_widget(StatScreen(name='stat'))
        return sm

if __name__ == '__main__':
    HabitTrackerApp().run()
```

---

### How It Works

1. **Database Module:**
   The `database.py` file defines a `Database` class that creates the required SQLite tables and provides methods to add, delete, update, and fetch habits as well as their tracking data.

2. **Kivy Application (`main.py`):**
   The application uses a `ScreenManager` to switch between three screens:
   - **TrackerScreen:** Displays a table with one row per habit and columns for the last 7 days. Each cell is a button that, when pressed, cycles its status (displayed with an emoji) and immediately updates the database.
   - **EditScreen:** Provides a text input to add new habits and displays the current habits along with a “Delete” button.
   - **StatScreen:** Fetches tracking data over the period from the start of the previous month to the end of the current month and builds a table with two rows (one for each month) to show the habit’s statistics. The cells’ background colors change based on the habit status (green for done, red for fail, white if not set).

3. **Running on Android:**
   You can package this Kivy application for Android using [Buildozer](https://github.com/kivy/buildozer) (or another tool from the Kivy ecosystem). Be sure to install the necessary dependencies and adjust the configuration as needed.

This is one possible solution; you may adjust the layouts, styles, or functionality to better suit your requirements.
