# 📋 Task Management System ( Ashutosh Singh)

A clean, modern, and user-friendly Task Management System built with a Flask backend and a responsive vanilla HTML/JS/CSS frontend. The application features separate views for **Administrators** (who manage tasks and assign them to employees) and **Employees** (who track and update progress on their assigned tasks).

---

## 🗺️ Project Architecture & Structure

The project has a unified structure where the Flask backend directly serves the frontend static assets.

```
project-root/
│
├── frontend/                     # Static Frontend Assets
│   ├── login.html                # Login screen
│   ├── dashboard.html            # Admin dashboard
│   ├── employee_dashboard.html   # Employee dashboard
│   ├── assets/
│   │   ├── favicon.png           # Custom brand icon
│   │   └── logo.png              # Brand logo
│   ├── css/
│   │   └── style.css             # Main stylesheet (Theme, animations, layouts)
│   └── js/
│       ├── login.js              # Login validation & auth integration
│       ├── dashboard.js          # Admin dashboard client logic
│       └── employee_dashboard.js # Employee dashboard client logic
│
├── backend/                      # Flask Backend Application
│   ├── run.py                    # Entry point for development server
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Env configuration template
│   └── task_management/          # Application package
│       ├── __init__.py           # Application Factory setup (create_app)
│       ├── config.py             # Config classes (Lax/Secure cookies)
│       ├── extensions.py         # SQLAlchemy & CORS extensions
│       ├── models/               # SQLAlchemy ORM Models
│       │   ├── user.py           # User definitions & credentials
│       │   ├── employee.py       # Employee profiles
│       │   ├── department.py     # Departments
│       │   ├── task.py           # Tasks
│       │   ├── task_assignment.py# Task assignments junction
│       │   └── activity_log.py   # Security & audit logs
│       ├── routes/               # Blueprints & Controllers
│       │   ├── auth.py           # Authentications & sessions
│       │   ├── employee.py       # Employee & department lists
│       │   ├── task.py           # Task CRUD APIs
│       │   └── assignment.py     # Assignment CRUD & status APIs
│       └── services/             # Business Logic Layer
│
└── README.md                     # This file
```

---

## 📊 Completed Milestones

All phases of the project implementation are **100% complete**:

- [x] **Phase 1: Mockup UIs** — Standalone login interface with local storage simulation.
- [x] **Phase 2: Database Schema** — MySQL ORM models configured via SQLAlchemy.
- [x] **Phase 3: Real Authentication** — Session-based cookie auth with `/api/auth/login` and `/api/auth/me`.
- [x] **Phase 4: Task CRUD APIs** — Full REST CRUD operations for task creation, retrieval, updates, and deletion.
- [x] **Phase 5: Auth Wiring** — Wired client-side login validation to real endpoints.
- [x] **Phase 6: Dashboards** — Dynamic Admin and Employee panels with real-time status/remarks progress updates.
- [x] **Phase 7: HCI Enhancements** — Upgraded fonts, hover indicators, top logout positions, and row click fill shortcuts.

---

## 🔑 Login Credentials (Pruned Sample Database)

The development database has been pruned to a clean, minimal set of entries for easy demo testing:

| Username | Password | Role | Employee Profile |
|---|---|---|---|
| `admin` | `admin123` | **Admin** | None |
| `aarav.sharma` | `Employee123` | **Employee** | Aarav Sharma (ML Engineer) |
| `rohan.patel` | `Employee123` | **Employee** | Rohan Patel (Office Assistant) |
| `ananya.sharma` | `Employee123` | **Employee** | Ananya Sharma (UI Designer) |

---

## 🛡️ Security Implementations
- **Secure Password Hashing**: Passwords are saved as secure cryptographic hashes using `scrypt` hashing algorithms. Plain-text credentials are never saved or exposed.
- **Session Isolation**: Sessions are signed cryptographically to prevent client-side modifications.
- **In-Transit Protection (HTTPS)**: Session cookies in the production configuration are locked with `SESSION_COOKIE_SECURE = True`, restricting transmission to encrypted SSL/TLS channels only.

---

## ⚙️ How to Setup and Run the Project

### 1. Database Setup
1. Create a MySQL database called `task_management_db`.
2. Configure credentials by copying `backend/.env.example` to `backend/.env` and updating the `SQLALCHEMY_DATABASE_URI` line:
   ```env
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://<user>:<password>@localhost:3306/task_management_db
   ```

### 2. Startup Server
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Activate the pre-configured Python virtual environment:
   ```bash
   venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python run.py
   ```
5. Open your web browser and go to **`http://127.0.0.1:5000/`**. The unified server will automatically serve the login page.

---

## 🧪 Testing and Verification
To run the automated integration tests and check API health, activate the virtual environment in `backend/` and run:
```bash
python test_backend_api.py
```
