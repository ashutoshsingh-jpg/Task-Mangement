"""ActivityLog model - audit trail entries for task assignments."""

from datetime import datetime

from task_management.extensions import db


class ActivityLog(db.Model):
    """Represents an activity_logs row from schema.sql."""

    __tablename__ = "activity_logs"

    id: int = db.Column(
        "log_id", db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True
    )
    assignment_id: int = db.Column(
        db.Integer, db.ForeignKey("task_assignments.assignment_id"), nullable=False
    )
    user_id: int = db.Column(
        "performed_by", db.Integer, db.ForeignKey("users.user_id"), nullable=False
    )
    action: str = db.Column(db.String(100), nullable=False)
    old_value: dict | None = db.Column(db.JSON, nullable=True)
    new_value: dict | None = db.Column(db.JSON, nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = db.relationship("User", back_populates="activity_logs")
    assignment = db.relationship("TaskAssignment")

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.id} action={self.action!r}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "user_id": self.user_id,
            "action": self.action,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
