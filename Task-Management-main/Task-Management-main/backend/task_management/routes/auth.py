"""
Authentication endpoints.

Wraps `task_management.services.auth_service`. Sessions (Flask's signed
cookie session) hold the logged-in user's id; there is no JWT layer
since none is pinned in requirements.txt.

Routes (mounted at /api/auth):
    POST /login               -- authenticate, start a session
    POST /logout                -- end the session
    POST /change-password        -- change the logged-in user's password
    GET  /me                       -- fetch the logged-in user's profile
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from task_management.routes import login_required
from task_management.services.auth_service import (
    AuthError,
    authenticate_user,
    change_password,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required."}), 400

    try:
        user = authenticate_user(username=username, password=password)
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 401

    session["user_id"] = user.id
    return jsonify(user.to_dict()), 200


@auth_bp.post("/logout")
@login_required
def logout(current_user):
    session.clear()
    return jsonify({"message": "Logged out."}), 200


@auth_bp.post("/change-password")
@login_required
def change_password_route(current_user):
    data = request.get_json(silent=True) or {}
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"error": "old_password and new_password are required."}), 400

    try:
        change_password(
            user_id=current_user.id,
            current_password=old_password,
            new_password=new_password,
        )
    except AuthError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"message": "Password updated."}), 200


@auth_bp.get("/me")
@login_required
def me(current_user):
    return jsonify(current_user.to_dict()), 200
