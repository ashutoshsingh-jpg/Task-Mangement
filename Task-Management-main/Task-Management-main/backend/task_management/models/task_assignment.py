"""TaskAssignment model - links a Task to the Employee assigned to it."""

from datetime import datetime

from task_management.extensions import db


class TaskAssignment(db.Model):
    """Represents a row in the task_assignments table."""

    __tablename__ = "task_assignments"

    id: int = db.Column("assignment_id", db.Integer, primary_key=True)
    employee_id: int = db.Column(
        db.Integer, db.ForeignKey("employees.employee_id"), nullable=False
    )
    task_id: int = db.Column(db.Integer, db.ForeignKey("tasks.task_id"), nullable=False)
    assigned_by: int = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    assigned_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    deadline: datetime | None = db.Column(db.DateTime, nullable=True)
    status: str = db.Column(
        db.Enum("Pending", "In Progress", "Completed", "On Hold", "Cancelled"),
        nullable=False,
        default="Pending",
    )
    completion_percentage: int = db.Column(db.SmallInteger, nullable=False, default=0)
    remarks: str | None = db.Column(db.Text, nullable=True)
    completed_at: datetime | None = db.Column(db.DateTime, nullable=True)
    updated_at: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    task = db.relationship("Task", back_populates="assignments")
    employee = db.relationship("Employee", back_populates="task_assignments")
    assigner = db.relationship("User", foreign_keys=[assigned_by])

    def __repr__(self) -> str:
        return (
            f"<TaskAssignment task_id={self.task_id} "
            f"employee_id={self.employee_id} status={self.status!r}>"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "task_id": self.task_id,
            "assigned_by": self.assigned_by,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "status": self.status,
            "completion_percentage": self.completion_percentage,
            "remarks": self.remarks,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
