# flask_backend.py
from flask_backend_core import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
