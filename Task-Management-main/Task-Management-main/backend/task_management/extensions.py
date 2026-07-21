"""Shared Flask extension instances.

Instantiated here (separately from the app factory) to avoid circular
imports: models and routes can import `db` directly without importing
`create_app` or the app instance itself.
"""

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy ORM instance, bound to the app later via `db.init_app(app)`.
db = SQLAlchemy()

# Flask-CORS instance, bound to the app later via `cors.init_app(app)`.
cors = CORS()
