-- ============================================================
-- Task Management System
-- Database Schema
-- Engine   : InnoDB
-- Charset  : utf8mb4
-- Collation: utf8mb4_unicode_ci
-- Target   : MySQL 8.0+
-- ============================================================

-- ------------------------------------------------------------
-- 1. Drop database if needed (commented out for safety)
-- ------------------------------------------------------------
-- DROP DATABASE IF EXISTS task_management_db;

-- ------------------------------------------------------------
-- 2. Create database
-- ------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS task_management_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 3. Use database
-- ------------------------------------------------------------
USE task_management_db;

-- ------------------------------------------------------------
-- 4. Disable foreign key checks
-- ------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 5. Drop existing tables in correct dependency order
-- ------------------------------------------------------------
DROP TABLE IF EXISTS activity_logs;
DROP TABLE IF EXISTS task_assignments;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;

-- ------------------------------------------------------------
-- 6. Enable foreign key checks
-- ------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- 7. Create every table
-- ------------------------------------------------------------

-- Create Users Table
-- Stores authentication and access-control data only.
CREATE TABLE users (
    user_id         INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    username        VARCHAR(50)     NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    role            ENUM('Admin', 'Employee')              NOT NULL,
    account_status  ENUM('Active', 'Inactive', 'Locked')   NOT NULL DEFAULT 'Active',
    last_login      DATETIME        NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_username (username)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- Create Departments Table
-- Master list of organizational departments.
CREATE TABLE departments (
    department_id   INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    department_name VARCHAR(100)   NOT NULL,
    description      VARCHAR(500)  NULL,
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (department_id),
    UNIQUE KEY uq_departments_department_name (department_name)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- Create Employees Table
-- Extends a user account with HR / profile information.
-- 1:1 relationship with users (only users with role = 'Employee'
-- are expected to have an employees record).
-- is_deleted supports soft-delete / archiving instead of hard deletes.
CREATE TABLE employees (
    employee_id     INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    user_id         INT UNSIGNED    NOT NULL,
    employee_code   VARCHAR(20)     NOT NULL,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    email           VARCHAR(100)    NOT NULL,
    phone           VARCHAR(20)     NOT NULL,
    department_id   INT UNSIGNED    NULL,
    designation     VARCHAR(100)    NULL,
    joining_date    DATE            NULL,
    status          ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (employee_id),
    UNIQUE KEY uq_employees_user_id (user_id),
    UNIQUE KEY uq_employees_employee_code (employee_code),
    UNIQUE KEY uq_employees_email (email),
    UNIQUE KEY uq_employees_phone (phone),

    -- Foreign Keys
    CONSTRAINT fk_employees_user_id
        FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_employees_department_id
        FOREIGN KEY (department_id) REFERENCES departments (department_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- Create Tasks Table
-- Master list of tasks that can later be assigned to employees.
-- is_deleted supports archiving task templates instead of hard deletes.
CREATE TABLE tasks (
    task_id          INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    task_title       VARCHAR(150)   NOT NULL,
    description      TEXT           NULL,
    notes            TEXT           NULL,
    priority         ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL DEFAULT 'Medium',
    is_deleted       BOOLEAN        NOT NULL DEFAULT FALSE,
    estimated_hours  TINYINT UNSIGNED NULL,
    created_by       INT UNSIGNED   NOT NULL,
    created_at       TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (task_id),
    UNIQUE KEY uq_tasks_task_title (task_title),

    -- Constraints
    CONSTRAINT chk_tasks_estimated_hours
        CHECK (estimated_hours > 0),

    -- Foreign Keys
    CONSTRAINT fk_tasks_created_by
        FOREIGN KEY (created_by) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- Create Task Assignments Table
-- Junction table linking employees to tasks, tracking status
-- and progress of each individual assignment.
CREATE TABLE task_assignments (
    assignment_id          INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    employee_id            INT UNSIGNED   NOT NULL,
    task_id                INT UNSIGNED   NOT NULL,
    assigned_by            INT UNSIGNED   NOT NULL,
    assigned_at            TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deadline               DATETIME       NULL,
    status                 ENUM('Pending', 'In Progress', 'Completed', 'On Hold', 'Cancelled')
                                           NOT NULL DEFAULT 'Pending',
    completion_percentage  TINYINT UNSIGNED NOT NULL DEFAULT 0,
    remarks                TEXT           NULL,
    completed_at           DATETIME       NULL,
    updated_at             TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                            ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (assignment_id),

    -- Constraints
    CONSTRAINT chk_task_assignments_completion_percentage
        CHECK (completion_percentage BETWEEN 0 AND 100),

    CONSTRAINT chk_task_assignments_deadline
        CHECK (deadline >= assigned_at),

    -- Foreign Keys
    CONSTRAINT fk_task_assignments_employee_id
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_task_assignments_task_id
        FOREIGN KEY (task_id) REFERENCES tasks (task_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_task_assignments_assigned_by
        FOREIGN KEY (assigned_by) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- Create Activity Logs Table
-- Audit trail capturing every change made to a task assignment.
-- old_value / new_value use JSON to capture structured before/after state.
CREATE TABLE activity_logs (
    log_id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    assignment_id   INT UNSIGNED    NOT NULL,
    performed_by    INT UNSIGNED    NOT NULL,
    action          VARCHAR(100)    NOT NULL,
    old_value       JSON            NULL,
    new_value       JSON            NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (log_id),

    -- Foreign Keys
    CONSTRAINT fk_activity_logs_assignment_id
        FOREIGN KEY (assignment_id) REFERENCES task_assignments (assignment_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_activity_logs_performed_by
        FOREIGN KEY (performed_by) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


-- ------------------------------------------------------------
-- 8. Create indexes
-- ------------------------------------------------------------

-- users
CREATE INDEX idx_users_username ON users (username);

-- employees
CREATE INDEX idx_employees_employee_code ON employees (employee_code);
CREATE INDEX idx_employees_first_name ON employees (first_name);
CREATE INDEX idx_employees_last_name ON employees (last_name);
CREATE INDEX idx_employee_name ON employees (first_name, last_name);

-- departments
CREATE INDEX idx_departments_department_name ON departments (department_name);

-- tasks
CREATE INDEX idx_tasks_task_title ON tasks (task_title);
CREATE INDEX idx_tasks_priority ON tasks (priority);

-- task_assignments
CREATE INDEX idx_task_assignments_status ON task_assignments (status);
CREATE INDEX idx_task_assignments_deadline ON task_assignments (deadline);
CREATE INDEX idx_assignment_employee_status ON task_assignments (employee_id, status);
CREATE INDEX idx_assignment_task_status ON task_assignments (task_id, status);

-- ------------------------------------------------------------
-- 9. Display success message
-- ------------------------------------------------------------
SELECT 'task_management_db schema created successfully.' AS status;

-- ------------------------------------------------------------
-- 10. Show tables
-- ------------------------------------------------------------
SHOW TABLES;
