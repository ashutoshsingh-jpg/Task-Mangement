"""Models package.

Imports every ORM model so they register with SQLAlchemy's metadata
when the package is imported (required for `db.create_all()` and
Alembic/Flask-Migrate autogeneration to see all tables).
"""

from task_management.models.activity_log import ActivityLog
from task_management.models.department import Department
from task_management.models.employee import Employee
from task_management.models.task import Task
from task_management.models.task_assignment import TaskAssignment
from task_management.models.user import User

__all__ = [
    "User",
    "Department",
    "Employee",
    "Task",
    "TaskAssignment",
    "ActivityLog",
]
