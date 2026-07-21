"""Employee model - profile information linked to a User and Department."""

from datetime import date, datetime

from task_management.extensions import db


class Employee(db.Model):
    """Represents an employee profile stored in the employees table."""

    __tablename__ = "employees"

    id: int = db.Column("employee_id", db.Integer, primary_key=True)
    user_id: int = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), unique=True, nullable=False
    )
    employee_code: str = db.Column(db.String(20), unique=True, nullable=False)
    first_name: str = db.Column(db.String(50), nullable=False)
    last_name: str = db.Column(db.String(50), nullable=False)
    email: str = db.Column(db.String(100), unique=True, nullable=False)
    phone: str = db.Column(db.String(20), unique=True, nullable=False)
    department_id: int | None = db.Column(
        db.Integer, db.ForeignKey("departments.department_id"), nullable=True
    )
    designation: str | None = db.Column(db.String(100), nullable=True)
    joining_date: date | None = db.Column(db.Date, nullable=True)
    status: str = db.Column(db.Enum("Active", "Inactive"), nullable=False, default="Active")
    is_deleted: bool = db.Column(db.Boolean, nullable=False, default=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: datetime = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = db.relationship("User", back_populates="employee")
    department = db.relationship("Department", back_populates="employees")
    task_assignments = db.relationship(
        "TaskAssignment", back_populates="employee", cascade="all, delete-orphan"
    )

    @property
    def position(self) -> str | None:
        return self.designation

    @position.setter
    def position(self, value: str | None) -> None:
        self.designation = value

    @property
    def hire_date(self) -> date | None:
        return self.joining_date

    @hire_date.setter
    def hire_date(self, value: date | None) -> None:
        self.joining_date = value

    def __repr__(self) -> str:
        return f"<Employee id={self.id} name={self.first_name!r} {self.last_name!r}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "employee_code": self.employee_code,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}",
            "email": self.email,
            "phone": self.phone,
            "department_id": self.department_id,
            "position": self.designation,
            "hire_date": self.joining_date.isoformat() if self.joining_date else None,
            "status": self.status,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
