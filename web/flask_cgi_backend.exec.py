#!/usr/bin/env python3
from web.flask_backend_core import create_app
from wsgiref.handlers import CGIHandler

app = None

def main():
    global app
    app = create_app()
    CGIHandler().run(app)

if __name__ == '__main__':
    main()
