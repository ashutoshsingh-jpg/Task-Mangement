"""Business logic layer.

Each module in this package encapsulates the business rules for one area
of the domain (auth, employees, tasks, assignments) and is the only layer
allowed to talk directly to the SQLAlchemy models. Route handlers should
call into these services rather than touching models/db.session directly.
"""

from __future__ import annotations

from typing import Optional

from task_management.extensions import db
from task_management.models.activity_log import ActivityLog

__all__ = ["log_activity"]


def log_activity(
    *,
    user_id: int,
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[str] = None,
) -> Optional[ActivityLog]:
    """Record an audit-trail entry.

    Shared by every service so that all state-changing operations are
    consistently logged. Does not commit the session itself — callers
    add this entry to the same transaction as the change it documents
    and commit once, so the audit record never exists without the
    change it describes (and vice versa).
    """
    if target_type != "TaskAssignment" or target_id is None:
        return None

    entry = ActivityLog(
        user_id=user_id,
        assignment_id=target_id,
        action=action,
        new_value={"details": details} if details else None,
    )
    db.session.add(entry)
    return entry
