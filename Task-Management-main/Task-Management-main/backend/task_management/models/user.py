"""User model - authentication credentials and role information."""

from datetime import datetime

from task_management.extensions import db


class User(db.Model):
    """Represents a login account stored in the schema.sql users table."""

    __tablename__ = "users"

    id: int = db.Column("user_id", db.Integer, primary_key=True)
    username: str = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(255), nullable=False)
    role: str = db.Column(db.Enum("Admin", "Employee"), nullable=False)
    account_status: str = db.Column(
        db.Enum("Active", "Inactive", "Locked"), nullable=False, default="Active"
    )
    last_login: datetime | None = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    employee = db.relationship(
        "Employee",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    activity_logs = db.relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role.lower() if self.role else None,
            "employee_id": self.employee.id if self.employee else None,
            "account_status": self.account_status,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
