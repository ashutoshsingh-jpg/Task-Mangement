"""
Employee endpoints.

Wraps `task_management.services.employee_service`. Mutating actions
(create/update/delete) are restricted to admin/manager roles; reads
are open to any authenticated user.

Routes (mounted at /api/employees):
    POST   /                              -- create an employee profile
    GET    /<int:employee_id>              -- fetch a single employee
    PUT    /<int:employee_id>               -- update an employee
    DELETE /<int:employee_id>                -- delete an employee
    GET    /department/<int:department_id>    -- list employees in a department
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from task_management.routes import login_required, roles_required
from task_management.services.employee_service import (
    EmployeeError,
    create_employee,
    delete_employee,
    get_employee,
    list_employees_by_department,
    update_employee,
)

employee_bp = Blueprint("employee", __name__)


@employee_bp.post("")
@login_required
@roles_required("admin", "manager")
def create(current_user):
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    department_id = data.get("department_id")
    employee_code = data.get("employee_code")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")

    if not all([user_id, department_id, employee_code, first_name, last_name, email, phone]):
        return (
            jsonify(
                {
                    "error": (
                        "user_id, department_id, employee_code, first_name, "
                        "last_name, email, and phone are required."
                    )
                }
            ),
            400,
        )

    try:
        employee = create_employee(
            acting_user_id=current_user.id,
            user_id=user_id,
            department_id=department_id,
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            position=data.get("position") or data.get("job_title"),
        )
    except EmployeeError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(employee.to_dict()), 201


@employee_bp.get("/<int:employee_id>")
@login_required
def get(employee_id: int, current_user):
    try:
        employee = get_employee(employee_id)
    except EmployeeError as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify(employee.to_dict()), 200


@employee_bp.put("/<int:employee_id>")
@login_required
@roles_required("admin", "manager")
def update(employee_id: int, current_user):
    data = request.get_json(silent=True) or {}
    allowed_fields = {
        "department_id",
        "first_name",
        "last_name",
        "employee_code",
        "email",
        "phone",
        "position",
        "status",
    }
    updates = {key: value for key, value in data.items() if key in allowed_fields}
    if "job_title" in data and "position" not in updates:
        updates["position"] = data["job_title"]

    try:
        employee = update_employee(
            acting_user_id=current_user.id,
            employee_id=employee_id,
            **updates,
        )
    except EmployeeError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(employee.to_dict()), 200


@employee_bp.delete("/<int:employee_id>")
@login_required
@roles_required("admin", "manager")
def delete(employee_id: int, current_user):
    try:
        delete_employee(acting_user_id=current_user.id, employee_id=employee_id)
    except EmployeeError as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify({"message": "Employee deleted."}), 200


@employee_bp.get("/department/<int:department_id>")
@login_required
def by_department(department_id: int, current_user):
    try:
        employees = list_employees_by_department(department_id)
    except EmployeeError as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify([employee.to_dict() for employee in employees]), 200


@employee_bp.get("")
@login_required
def list_all_employees(current_user):
    from task_management.models.employee import Employee
    employees = Employee.query.filter_by(is_deleted=False).all()
    return jsonify([emp.to_dict() for emp in employees]), 200


@employee_bp.get("/departments")
@login_required
def list_departments(current_user):
    from task_management.models.department import Department
    departments = Department.query.all()
    return jsonify([dept.to_dict() for dept in departments]), 200
