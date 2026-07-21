"""
Blueprint registration for the task_management API.

This module exposes `register_routes(app)`, called from
`task_management/__init__.py::create_app()`, which attaches every
blueprint to the Flask application under a common `/api` prefix.

It also defines two lightweight, session-based access-control
decorators shared by every route module:

    @login_required   -- rejects the request unless a user is logged in
    @roles_required(*roles) -- additionally restricts by `User.role`

Session-based auth is used (rather than JWT) because no token library
is pinned in requirements.txt. `login_required` expects the
authenticated user's id to be stored at `session["user_id"]`, which
`routes.auth.login` is responsible for setting.
"""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import Flask, jsonify, session

from task_management.services.auth_service import AuthError, get_user_by_id


def login_required(view_func: Callable) -> Callable:
    """Reject the request with 401 unless a user is logged in."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify({"error": "Authentication required."}), 401

        try:
            user = get_user_by_id(user_id)
        except AuthError:
            session.clear()
            return jsonify({"error": "Authentication required."}), 401

        # Stash the loaded user on the request context via flask.g-like
        # pattern without importing g twice across modules.
        kwargs["current_user"] = user
        return view_func(*args, **kwargs)

    return wrapper


def roles_required(*roles: str) -> Callable:
    """Reject the request with 403 unless the logged-in user's role matches.

    Must be stacked underneath @login_required, e.g.:

        @app.route(...)
        @login_required
        @roles_required("admin", "manager")
        def view(current_user): ...
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            allowed_roles = {role.lower() for role in roles}
            current_role = current_user.role.lower() if current_user and current_user.role else None
            if current_role not in allowed_roles:
                return jsonify({"error": "Insufficient permissions."}), 403
            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def register_routes(app: Flask) -> None:
    """Register all API blueprints on the given Flask app instance."""

    from task_management.routes.auth import auth_bp
    from task_management.routes.employee import employee_bp
    from task_management.routes.task import task_bp
    from task_management.routes.assignment import assignment_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(employee_bp, url_prefix="/api/employees")
    app.register_blueprint(task_bp, url_prefix="/api/tasks")
    app.register_blueprint(assignment_bp, url_prefix="/api/assignments")
