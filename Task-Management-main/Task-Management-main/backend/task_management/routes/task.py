"""
Task endpoints.

Wraps `task_management.services.task_service`. `created_by` is always
taken from the logged-in session, never from the request body, so a
user cannot forge task ownership.

Routes (mounted at /api/tasks):
    POST   /                 -- create a task (creator = current user)
    GET    /<int:task_id>     -- fetch a single task
    PUT    /<int:task_id>      -- update a task
    DELETE /<int:task_id>       -- delete a task
    GET    /                     -- list tasks, optionally filtered by
                                     query params: status, priority, created_by
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from task_management.routes import login_required
from task_management.services.task_service import (
    TaskError,
    create_task,
    delete_task,
    get_task,
    list_tasks,
    update_task,
)

task_bp = Blueprint("task", __name__)


@task_bp.post("")
@login_required
def create(current_user):
    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not title:
        return jsonify({"error": "title is required."}), 400

    try:
        task = create_task(
            title=title,
            description=data.get("description"),
            notes=data.get("notes"),
            priority=data.get("priority", "medium"),
            estimated_hours=data.get("estimated_hours"),
            created_by=current_user.id,
        )
    except TaskError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(task.to_dict()), 201


@task_bp.get("/<int:task_id>")
@login_required
def get(task_id: int, current_user):
    try:
        task = get_task(task_id)
    except TaskError as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify(task.to_dict()), 200


@task_bp.put("/<int:task_id>")
@login_required
def update(task_id: int, current_user):
    data = request.get_json(silent=True) or {}
    allowed_fields = {
        "title",
        "description",
        "notes",
        "priority",
        "estimated_hours",
    }
    updates = {key: value for key, value in data.items() if key in allowed_fields}

    try:
        task = update_task(
            acting_user_id=current_user.id,
            task_id=task_id,
            **updates,
        )
    except TaskError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(task.to_dict()), 200


@task_bp.delete("/<int:task_id>")
@login_required
def delete(task_id: int, current_user):
    try:
        delete_task(acting_user_id=current_user.id, task_id=task_id)
    except TaskError as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify({"message": "Task deleted."}), 200


@task_bp.get("")
@login_required
def list_all(current_user):
    filters = {}
    for key in ("priority", "created_by"):
        value = request.args.get(key)
        if value is not None:
            filters[key] = value

    try:
        tasks = list_tasks(**filters)
    except TaskError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify([task.to_dict() for task in tasks]), 200
