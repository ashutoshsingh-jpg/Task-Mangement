"""Task assignment business logic (the Task <-> Employee join)."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from task_management.extensions import db
from task_management.models.employee import Employee
from task_management.models.task import Task
from task_management.models.task_assignment import TaskAssignment
from task_management.services import log_activity

VALID_STATUSES = {"Pending", "In Progress", "Completed", "On Hold", "Cancelled"}


def normalize_status(status: str) -> str:
    normalized = status.strip().lower().replace("_", " ")
    mapping = {
        "assigned": "Pending",
        "pending": "Pending",
        "in progress": "In Progress",
        "completed": "Completed",
        "on hold": "On Hold",
        "cancelled": "Cancelled",
        "canceled": "Cancelled",
        "declined": "Cancelled",
    }
    return mapping.get(normalized, status)


class AssignmentError(Exception):
    """Raised for any task-assignment business-rule violation."""


def assign_task_to_employee(
    *, acting_user_id: int, task_id: int, employee_id: int
) -> TaskAssignment:
    """Assign a task to an employee.

    Raises AssignmentError if the task/employee don't exist, or the pair
    is already assigned (mirrors the model's unique constraint).
    """
    if Task.query.get(task_id) is None:
        raise AssignmentError(f"No task found with id={task_id}.")
    if Employee.query.get(employee_id) is None:
        raise AssignmentError(f"No employee found with id={employee_id}.")
    if TaskAssignment.query.filter_by(task_id=task_id, employee_id=employee_id).first():
        raise AssignmentError(
            f"Task id={task_id} is already assigned to employee id={employee_id}."
        )

    assignment = TaskAssignment(
        task_id=task_id,
        employee_id=employee_id,
        assigned_by=acting_user_id,
        status="Pending",
        assigned_at=datetime.utcnow(),
    )
    db.session.add(assignment)
    db.session.flush()

    log_activity(
        user_id=acting_user_id,
        action="task_assigned",
        target_type="TaskAssignment",
        target_id=assignment.id,
        details=f"task_id={task_id}, employee_id={employee_id}",
    )
    db.session.commit()
    return assignment


def get_assignment(assignment_id: int) -> TaskAssignment:
    """Fetch an assignment by primary key, raising AssignmentError if not found."""
    assignment: Optional[TaskAssignment] = TaskAssignment.query.get(assignment_id)
    if assignment is None:
        raise AssignmentError(f"No task assignment found with id={assignment_id}.")
    return assignment


def update_assignment_status(
    *,
    acting_user_id: int,
    assignment_id: int,
    status: str,
    completion_percentage: Optional[int] = None,
    remarks: Optional[str] = None,
) -> TaskAssignment:
    """Update an assignment's status (e.g. moving it to 'completed').

    Stamps completed_at when the status transitions to 'completed'.
    """
    status = normalize_status(status)
    if status not in VALID_STATUSES:
        raise AssignmentError(f"Invalid status '{status}'. Must be one of {sorted(VALID_STATUSES)}.")

    assignment = get_assignment(assignment_id)
    assignment.status = status
    if status == "Completed":
        assignment.completed_at = datetime.utcnow()
        assignment.completion_percentage = 100
    elif completion_percentage is not None:
        if not (0 <= completion_percentage <= 100):
            raise AssignmentError("Completion percentage must be between 0 and 100.")
        assignment.completion_percentage = completion_percentage

    if remarks is not None:
        assignment.remarks = remarks

    log_activity(
        user_id=acting_user_id,
        action="task_assignment_status_updated",
        target_type="TaskAssignment",
        target_id=assignment.id,
        details=f"status={status}, completion={assignment.completion_percentage}",
    )
    db.session.commit()
    return assignment


def remove_assignment(*, acting_user_id: int, assignment_id: int) -> None:
    """Unassign a task from an employee."""
    assignment = get_assignment(assignment_id)
    db.session.delete(assignment)
    log_activity(
        user_id=acting_user_id,
        action="task_assignment_removed",
        target_type="TaskAssignment",
        target_id=assignment_id,
    )
    db.session.commit()


def list_assignments_for_employee(employee_id: int) -> List[TaskAssignment]:
    """Return all task assignments for a given employee."""
    if Employee.query.get(employee_id) is None:
        raise AssignmentError(f"No employee found with id={employee_id}.")
    return TaskAssignment.query.filter_by(employee_id=employee_id).all()


def list_assignments_for_task(task_id: int) -> List[TaskAssignment]:
    """Return all assignments (employees) for a given task."""
    if Task.query.get(task_id) is None:
        raise AssignmentError(f"No task found with id={task_id}.")
    return TaskAssignment.query.filter_by(task_id=task_id).all()
