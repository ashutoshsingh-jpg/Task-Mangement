"""Development server entry point.

Creates the Flask application via the factory function and runs it.
Actual app configuration, extension setup, and blueprint registration
live inside the `task_management` package (see `task_management/__init__.py`).
"""

from task_management import create_app

# Instantiate the Flask app using the application factory pattern.
app = create_app()

if __name__ == "__main__":
    # debug=True is safe here only because FLASK_ENV controls the real
    # environment; Config classes decide production-readiness.
    app.run(debug=True)
