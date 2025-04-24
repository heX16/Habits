#!/usr/bin/env python3
from web.flask_backend_core import create_app

app = None

def main():
    global app
    app = create_app()
    app.run(debug=True)

if __name__ == '__main__':
    main()
