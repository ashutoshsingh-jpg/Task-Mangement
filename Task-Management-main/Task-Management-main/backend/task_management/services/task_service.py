"""Task business logic."""

from __future__ import annotations

from typing import List, Optional

from task_management.extensions import db
from task_management.models.task import Task
from task_management.models.user import User
from task_management.services import log_activity

VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}


def normalize_priority(priority: str) -> str:
    normalized = priority.strip().lower()
    mapping = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical",
        "urgent": "Critical",
    }
    return mapping.get(normalized, priority)


class TaskError(Exception):
    """Raised for any task business-rule violation."""


def create_task(
    *,
    created_by: int,
    title: str,
    description: Optional[str] = None,
    priority: str = "Medium",
    notes: Optional[str] = None,
    estimated_hours: Optional[int] = None,
) -> Task:
    """Create a new task owned by the given user.

    Raises TaskError if the creating user doesn't exist or the priority
    is not one of the recognized values.
    """
    if User.query.get(created_by) is None:
        raise TaskError(f"No user found with id={created_by}.")
    priority = normalize_priority(priority)
    if priority not in VALID_PRIORITIES:
        raise TaskError(f"Invalid priority '{priority}'. Must be one of {sorted(VALID_PRIORITIES)}.")

    task = Task(
        title=title,
        description=description,
        notes=notes,
        priority=priority,
        estimated_hours=estimated_hours,
        created_by=created_by,
    )
    db.session.add(task)
    db.session.flush()

    log_activity(user_id=created_by, action="task_created", target_type="Task", target_id=task.id)
    db.session.commit()
    return task


def get_task(task_id: int) -> Task:
    """Fetch a task by primary key, raising TaskError if not found."""
    task: Optional[Task] = Task.query.get(task_id)
    if task is None:
        raise TaskError(f"No task found with id={task_id}.")
    return task


def update_task(
    *,
    acting_user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    notes: Optional[str] = None,
    estimated_hours: Optional[int] = None,
) -> Task:
    """Update mutable fields on a task. Only provided fields change."""
    task = get_task(task_id)

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if notes is not None:
        task.notes = notes
    if priority is not None:
        priority = normalize_priority(priority)
        if priority not in VALID_PRIORITIES:
            raise TaskError(f"Invalid priority '{priority}'. Must be one of {sorted(VALID_PRIORITIES)}.")
        task.priority = priority
    if estimated_hours is not None:
        task.estimated_hours = estimated_hours

    log_activity(
        user_id=acting_user_id, action="task_updated", target_type="Task", target_id=task.id
    )
    db.session.commit()
    return task


def delete_task(*, acting_user_id: int, task_id: int) -> None:
    """Delete a task and its assignments (cascade is handled at the DB/model level)."""
    task = get_task(task_id)
    db.session.delete(task)
    log_activity(user_id=acting_user_id, action="task_deleted", target_type="Task", target_id=task_id)
    db.session.commit()


def list_tasks(*, created_by: Optional[int] = None, priority: Optional[str] = None) -> List[Task]:
    """Return non-deleted tasks, optionally filtered by creator or priority."""
    query = Task.query
    query = query.filter_by(is_deleted=False)
    if created_by is not None:
        query = query.filter_by(created_by=created_by)
    if priority is not None:
        priority = normalize_priority(priority)
        if priority not in VALID_PRIORITIES:
            raise TaskError(f"Invalid priority '{priority}'. Must be one of {sorted(VALID_PRIORITIES)}.")
        query = query.filter_by(priority=priority)
    return query.all()
