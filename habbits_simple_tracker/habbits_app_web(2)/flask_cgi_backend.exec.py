#!/usr/bin/env python3
from flask_backend_core import create_app
from wsgiref.handlers import CGIHandler

app = create_app()

if __name__ == '__main__':
    CGIHandler().run(app)
