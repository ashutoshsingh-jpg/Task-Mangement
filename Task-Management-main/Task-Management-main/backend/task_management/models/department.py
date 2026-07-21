"""Department model - organizational grouping for employees."""

from datetime import datetime

from task_management.extensions import db


class Department(db.Model):
    """Represents a company department stored in the departments table."""

    __tablename__ = "departments"

    id: int = db.Column("department_id", db.Integer, primary_key=True)
    name: str = db.Column("department_name", db.String(100), unique=True, nullable=False)
    description: str | None = db.Column(db.String(500), nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    employees = db.relationship("Employee", back_populates="department")

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
