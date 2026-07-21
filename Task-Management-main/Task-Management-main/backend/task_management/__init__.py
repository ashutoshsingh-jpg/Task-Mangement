"""Application factory.

Creates and configures the Flask app: loads the right Config class,
binds shared extensions (db, cors) from `extensions.py`, verifies the
MySQL connection on startup, and exposes a `/health` endpoint for
ongoing connectivity checks.
"""

import os

from flask import Flask, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .config import Config, DevelopmentConfig, ProductionConfig
from .extensions import db, cors
from .routes import register_routes


def create_app() -> Flask:
    # Resolve absolute path of the frontend folder (two levels up from this file)
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")

    # Select config class based on FLASK_ENV (set in .env / environment).
    # Defaults to development if not specified.
    env = os.environ.get("FLASK_ENV", "development").lower()
    config_class = ProductionConfig if env == "production" else DevelopmentConfig
    app.config.from_object(config_class)

    # Bind extensions to this app instance (factory pattern requires
    # init_app rather than passing `app` at instantiation time).
    db.init_app(app)
    cors.init_app(
        app,
        origins=app.config.get("CORS_ORIGINS"),
        supports_credentials=True,
    )

    # Register all API blueprints
    register_routes(app)

    # --- Startup DB connectivity check -------------------------------
    # Runs once when the app is created so misconfiguration (bad
    # credentials, MySQL not running, wrong host/port, etc.) is caught
    # immediately in the logs instead of surfacing later on first request.
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            db.session.remove()
            app.logger.info("Database connection established successfully.")
        except SQLAlchemyError as exc:
            app.logger.warning("Database connection failed at startup: %s", exc)

    # --- Health check endpoint ----------------------------------------
    @app.get("/health")
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "success", "database": "connected"}), 200
        except SQLAlchemyError as exc:
            return (
                jsonify(
                    {
                        "status": "error",
                        "database": "disconnected",
                        "message": str(exc),
                    }
                ),
                500,
            )

    # --- Root route redirecting to login.html --------------------------
    @app.route("/")
    def index():
        return app.send_static_file("login.html")

    return app
