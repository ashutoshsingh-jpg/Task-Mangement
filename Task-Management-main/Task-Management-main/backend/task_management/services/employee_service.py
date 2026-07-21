"""Employee profile business logic."""

from __future__ import annotations

from typing import List, Optional

from task_management.extensions import db
from task_management.models.department import Department
from task_management.models.employee import Employee
from task_management.models.user import User
from task_management.services import log_activity


class EmployeeError(Exception):
    """Raised for any employee/department business-rule violation."""


def create_employee(
    *,
    acting_user_id: int,
    user_id: int,
    department_id: int,
    employee_code: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    position: Optional[str] = None,
) -> Employee:
    """Create an employee profile linked 1:1 to an existing user.

    Raises EmployeeError if the user or department doesn't exist, or the
    user already has an employee profile.
    """
    if User.query.get(user_id) is None:
        raise EmployeeError(f"No user found with id={user_id}.")
    if Department.query.get(department_id) is None:
        raise EmployeeError(f"No department found with id={department_id}.")
    if Employee.query.filter_by(user_id=user_id).first() is not None:
        raise EmployeeError(f"User id={user_id} already has an employee profile.")

    employee = Employee(
        user_id=user_id,
        department_id=department_id,
        employee_code=employee_code,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        position=position,
    )
    db.session.add(employee)
    db.session.flush()

    log_activity(
        user_id=acting_user_id,
        action="employee_created",
        target_type="Employee",
        target_id=employee.id,
    )
    db.session.commit()
    return employee


def get_employee(employee_id: int) -> Employee:
    """Fetch an employee by primary key, raising EmployeeError if not found."""
    employee: Optional[Employee] = Employee.query.get(employee_id)
    if employee is None:
        raise EmployeeError(f"No employee found with id={employee_id}.")
    return employee


def update_employee(
    *,
    acting_user_id: int,
    employee_id: int,
    department_id: Optional[int] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    employee_code: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    position: Optional[str] = None,
    status: Optional[str] = None,
) -> Employee:
    """Update mutable fields on an employee profile. Only provided fields change."""
    employee = get_employee(employee_id)

    if department_id is not None:
        if Department.query.get(department_id) is None:
            raise EmployeeError(f"No department found with id={department_id}.")
        employee.department_id = department_id
    if first_name is not None:
        employee.first_name = first_name
    if last_name is not None:
        employee.last_name = last_name
    if employee_code is not None:
        employee.employee_code = employee_code
    if email is not None:
        employee.email = email
    if phone is not None:
        employee.phone = phone
    if position is not None:
        employee.position = position
    if status is not None:
        employee.status = status

    log_activity(
        user_id=acting_user_id,
        action="employee_updated",
        target_type="Employee",
        target_id=employee.id,
    )
    db.session.commit()
    return employee


def delete_employee(*, acting_user_id: int, employee_id: int) -> None:
    """Delete an employee profile.

    Raises EmployeeError if the employee still has task assignments, since
    those must be reassigned or removed first.
    """
    employee = get_employee(employee_id)
    if employee.task_assignments:
        raise EmployeeError(
            f"Cannot delete employee id={employee_id}: still has active task assignments."
        )

    db.session.delete(employee)
    log_activity(
        user_id=acting_user_id,
        action="employee_deleted",
        target_type="Employee",
        target_id=employee_id,
    )
    db.session.commit()


def list_employees_by_department(department_id: int) -> List[Employee]:
    """Return all employees belonging to a given department."""
    if Department.query.get(department_id) is None:
        raise EmployeeError(f"No department found with id={department_id}.")
    return Employee.query.filter_by(department_id=department_id).all()
