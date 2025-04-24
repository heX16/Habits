
Struct:
```
project/
├── flask_backend.py               # Wrapper for running in standard mode
├── flask_cgi_backend.exec.py      # Wrapper for CGI mode
├── flask_backend_core.py          # Flask routes and middleware (calls core functions)
├── habits_core.py                # Core business logic and database operations
├── database.db                    # (Automatically created on first run)
├── templates/
│   ├── index.html                 # Main page (habit tracker)
│   └── edit.html                  # Habit editing page
└── static/
    ├── script.js                  # Main page JS
    ├── edit.js                    # Edit page JS
    └── style.css                  # CSS styles

```

req:
```
pip install db-sqlite3
pip install flask
```


