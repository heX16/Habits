#!/usr/bin/env python3

from web.flask_backend_core import create_app

# Module-level app for Flask CLI / systemd:
#   python -m flask --app web.flask_backend:app run ...
# In that mode Flask imports this module and runs `app` itself; main() is not called.
app = create_app()

def main():
    # Console/debug entry point only (e.g. python -m web.flask_backend or run_web.py).
    # Not used when the app is started via Flask CLI or systemd.
    app.run(debug=True)

if __name__ == '__main__':
    main()
