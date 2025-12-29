from app import app

# For WSGI servers (gunicorn, uWSGI, waitress) we expose the `app` object.
application = app
