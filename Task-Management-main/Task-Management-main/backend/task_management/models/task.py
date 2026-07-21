"""Task model - a unit of work that can be assigned to employees."""

from datetime import datetime

from task_management.extensions import db


class Task(db.Model):
    """Represents a task stored in the tasks table."""

    __tablename__ = "tasks"

    id: int = db.Column("task_id", db.Integer, primary_key=True)
    title: str = db.Column("task_title", db.String(150), unique=True, nullable=False)
    description: str | None = db.Column(db.Text, nullable=True)
    notes: str | None = db.Column(db.Text, nullable=True)
    priority: str = db.Column(
        db.Enum("Low", "Medium", "High", "Critical"), nullable=False, default="Medium"
    )
    is_deleted: bool = db.Column(db.Boolean, nullable=False, default=False)
    estimated_hours: int | None = db.Column(db.SmallInteger, nullable=True)
    created_by: int = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    creator = db.relationship("User", foreign_keys=[created_by])
    assignments = db.relationship(
        "TaskAssignment", back_populates="task", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} priority={self.priority!r}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "notes": self.notes,
            "priority": self.priority,
            "is_deleted": self.is_deleted,
            "estimated_hours": self.estimated_hours,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
