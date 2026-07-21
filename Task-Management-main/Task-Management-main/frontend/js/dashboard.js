/**
 * Admin Dashboard Module
 * Custom JavaScript (Vanilla ES6)
 */

const API_BASE_URL = (window.location.protocol === "file:")
  ? "http://127.0.0.1:5000/api"
  : window.location.origin + "/api";

let currentUser = null;
let tasks = [];
let employees = [];
let assignments = [];

// DOM Elements
let elements = {};

document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  checkAuth();
  setupEventListeners();
});

function cacheElements() {
  elements = {
    sidebarToggle: document.getElementById("sidebarToggle"),
    sidebar: document.getElementById("sidebar"),
    logoutBtn: document.getElementById("logoutBtn"),
    currentUserName: document.getElementById("currentUserName"),
    currentUserRole: document.getElementById("currentUserRole"),
    
    // Metrics
    metricTotalTasks: document.getElementById("metricTotalTasks"),
    metricPendingAssignments: document.getElementById("metricPendingAssignments"),
    metricCompletedTasks: document.getElementById("metricCompletedTasks"),
    
    // Tasks Registry
    tasksTableBody: document.getElementById("tasksTableBody"),
    btnAddTask: document.getElementById("btnAddTask"),
    taskModal: new bootstrap.Modal(document.getElementById("taskModal")),
    taskModalLabel: document.getElementById("taskModalLabel"),
    taskForm: document.getElementById("taskForm"),
    modalTaskId: document.getElementById("modalTaskId"),
    taskTitleInput: document.getElementById("taskTitleInput"),
    taskDescInput: document.getElementById("taskDescInput"),
    taskPrioritySelect: document.getElementById("taskPrioritySelect"),
    taskHoursInput: document.getElementById("taskHoursInput"),
    btnSubmitTask: document.getElementById("btnSubmitTask"),
    
    // Assignment Form
    assignmentForm: document.getElementById("assignmentForm"),
    assignTaskSelect: document.getElementById("assignTaskSelect"),
    assignEmployeeSelect: document.getElementById("assignEmployeeSelect"),
    displayTaskId: document.getElementById("displayTaskId"),
    completedSelect: document.getElementById("completedSelect"),
    
    // Assignments List
    assignmentsTableBody: document.getElementById("assignmentsTableBody"),
    
    // Toast
    toast: new bootstrap.Toast(document.getElementById("statusToast")),
    toastMessage: document.getElementById("toastMessage"),
    toastContainer: document.getElementById("statusToast")
  };
}

function checkAuth() {
  fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    credentials: "include"
  })
  .then(res => {
    if (!res.ok) throw new Error("Unauthorized");
    return res.json();
  })
  .then(user => {
    if (user.role !== "admin") {
      // Employees are directed to employee dashboard
      window.location.href = "employee_dashboard.html";
      return;
    }
    currentUser = user;
    elements.currentUserName.textContent = user.username;
    elements.currentUserRole.textContent = "Admin";
    loadDashboardData();
  })
  .catch(() => {
    window.location.href = "login.html";
  });
}

function setupEventListeners() {
  // Mobile sidebar toggle
  elements.sidebarToggle.addEventListener("click", () => {
    elements.sidebar.classList.toggle("show");
  });

  // Logout handler
  elements.logoutBtn.addEventListener("click", handleLogout);

  // Reset modal on opening for "Add Task"
  elements.btnAddTask.addEventListener("click", () => {
    elements.taskForm.reset();
    elements.modalTaskId.value = "";
    elements.taskModalLabel.textContent = "Create New Task";
  });

  // Submit task (create or edit)
  elements.taskForm.addEventListener("submit", handleTaskSubmit);

  // Submit task assignment
  elements.assignmentForm.addEventListener("submit", handleAssignmentSubmit);

  // Dynamically update task Id text when task selection changes (Sketch UI)
  elements.assignTaskSelect.addEventListener("change", (e) => {
    elements.displayTaskId.textContent = e.target.value || "-";
  });
}

function loadDashboardData() {
  Promise.all([
    fetchTasks(),
    fetchEmployees(),
    fetchAssignments()
  ])
  .then(() => {
    updateMetrics();
    renderTasks();
    renderAssignments();
    populateSelects();
  })
  .catch(err => {
    showToast("Error loading dashboard data: " + err.message, false);
  });
}

// ==========================================================================
// API Calls
// ==========================================================================

function fetchTasks() {
  return fetch(`${API_BASE_URL}/tasks`, { credentials: "include" })
    .then(res => res.json())
    .then(data => { tasks = data; });
}

function fetchEmployees() {
  return fetch(`${API_BASE_URL}/employees`, { credentials: "include" })
    .then(res => res.json())
    .then(data => { employees = data; });
}

function fetchAssignments() {
  return fetch(`${API_BASE_URL}/assignments`, { credentials: "include" })
    .then(res => res.json())
    .then(data => { assignments = data; });
}

function handleLogout() {
  fetch(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
    credentials: "include"
  })
  .then(() => {
    localStorage.clear();
    window.location.href = "login.html";
  });
}

// ==========================================================================
// Render Functions
// ==========================================================================

function renderTasks() {
  const tbody = elements.tasksTableBody;
  if (tasks.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-muted">No tasks available. Add one!</td></tr>`;
    return;
  }

  tbody.innerHTML = tasks.map(task => `
    <tr>
      <td onclick="selectTaskForManagement(${task.id})" title="Click to auto-fill in Task Management form" style="cursor: pointer;">
        <div class="fw-bold text-primary">${escapeHTML(task.title)}</div>
        <div class="small text-muted text-truncate" style="max-width: 250px;">${escapeHTML(task.description || 'No description')}</div>
      </td>
      <td><span class="badge-status ${task.priority.toLowerCase()}">${task.priority}</span></td>
      <td>${task.estimated_hours || '-'} hrs</td>
      <td>
        <button class="btn btn-sm btn-outline-secondary me-1" onclick="editTask(${task.id})"><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})"><i class="bi bi-trash"></i></button>
      </td>
    </tr>
  `).join("");
}

function renderAssignments() {
  const tbody = elements.assignmentsTableBody;
  if (assignments.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-muted">No task assignments.</td></tr>`;
    return;
  }

  tbody.innerHTML = assignments.map(a => `
    <tr>
      <td class="fw-bold">${escapeHTML(a.task_title)}</td>
      <td>${escapeHTML(a.employee_name)}</td>
      <td><span class="badge-status ${a.status.toLowerCase().replace(" ", "-")}">${a.status}</span></td>
      <td>
        <button class="btn btn-sm btn-outline-danger" onclick="removeAssignment(${a.id})"><i class="bi bi-x-circle"></i></button>
      </td>
    </tr>
  `).join("");
}

function populateSelects() {
  // Populate Tasks
  elements.assignTaskSelect.innerHTML = `<option value="" disabled selected>Select a task...</option>` + 
    tasks.map(t => `<option value="${t.id}">${escapeHTML(t.title)} (${t.priority})</option>`).join("");
    
  // Populate Employees
  elements.assignEmployeeSelect.innerHTML = `<option value="" disabled selected>Select an assignee...</option>` + 
    employees.map(e => `<option value="${e.id}">${escapeHTML(e.full_name)} - ${escapeHTML(e.position || 'Employee')}</option>`).join("");
}

function updateMetrics() {
  elements.metricTotalTasks.textContent = tasks.length;
  
  const pendingCount = assignments.filter(a => a.status !== "Completed" && a.status !== "Cancelled").length;
  elements.metricPendingAssignments.textContent = pendingCount;
  
  const completedCount = assignments.filter(a => a.status === "Completed").length;
  elements.metricCompletedTasks.textContent = completedCount;
}

// ==========================================================================
// Form Submissions & Actions
// ==========================================================================

function handleTaskSubmit(e) {
  e.preventDefault();
  
  const taskId = elements.modalTaskId.value;
  const isEdit = taskId !== "";
  
  const taskData = {
    title: elements.taskTitleInput.value.trim(),
    description: elements.taskDescInput.value.trim(),
    priority: elements.taskPrioritySelect.value,
    estimated_hours: elements.taskHoursInput.value ? parseInt(elements.taskHoursInput.value) : null
  };

  const url = isEdit ? `${API_BASE_URL}/tasks/${taskId}` : `${API_BASE_URL}/tasks`;
  const method = isEdit ? "PUT" : "POST";

  fetch(url, {
    method: method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(taskData),
    credentials: "include"
  })
  .then(res => {
    if (!res.ok) return res.json().then(e => { throw new Error(e.error); });
    return res.json();
  })
  .then(() => {
    elements.taskModal.hide();
    showToast(isEdit ? "Task updated." : "Task created.", true);
    loadDashboardData();
  })
  .catch(err => {
    showToast(err.message || "Failed to save task.", false);
  });
}

function handleAssignmentSubmit(e) {
  e.preventDefault();

  const task_id = parseInt(elements.assignTaskSelect.value);
  const employee_id = parseInt(elements.assignEmployeeSelect.value);
  const completedVal = elements.completedSelect.value === "true";

  if (isNaN(task_id) || isNaN(employee_id)) {
    showToast("Please select both a task and an employee.", false);
    return;
  }

  const existing = assignments.find(a => a.task_id === task_id && a.employee_id === employee_id);

  if (existing) {
    const status = completedVal ? "Completed" : "In Progress";
    fetch(`${API_BASE_URL}/assignments/${existing.id}/status`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
      credentials: "include"
    })
    .then(res => {
      if (!res.ok) return res.json().then(e => { throw new Error(e.error); });
      return res.json();
    })
    .then(() => {
      elements.assignmentForm.reset();
      elements.displayTaskId.textContent = "-";
      showToast("Assignment status updated successfully.", true);
      loadDashboardData();
    })
    .catch(err => {
      showToast(err.message || "Update assignment failed.", false);
    });
  } else {
    fetch(`${API_BASE_URL}/assignments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id, employee_id }),
      credentials: "include"
    })
    .then(res => {
      if (!res.ok) return res.json().then(e => { throw new Error(e.error); });
      return res.json();
    })
    .then(newAssign => {
      if (completedVal) {
        return fetch(`${API_BASE_URL}/assignments/${newAssign.id}/status`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "Completed" }),
          credentials: "include"
        }).then(res => {
          if (!res.ok) return res.json().then(e => { throw new Error(e.error); });
          return res.json();
        });
      }
      return newAssign;
    })
    .then(() => {
      elements.assignmentForm.reset();
      elements.displayTaskId.textContent = "-";
      showToast("Task assigned successfully.", true);
      loadDashboardData();
    })
    .catch(err => {
      showToast(err.message || "Assignment failed.", false);
    });
  }
}

// Global actions exposed to onclick attributes
window.editTask = function(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;

  elements.modalTaskId.value = task.id;
  elements.taskTitleInput.value = task.title;
  elements.taskDescInput.value = task.description || "";
  elements.taskPrioritySelect.value = task.priority;
  elements.taskHoursInput.value = task.estimated_hours || "";
  
  elements.taskModalLabel.textContent = "Edit Task";
  elements.taskModal.show();
};

window.deleteTask = function(id) {
  if (!confirm("Are you sure you want to delete this task? This will remove related assignments.")) return;

  fetch(`${API_BASE_URL}/tasks/${id}`, {
    method: "DELETE",
    credentials: "include"
  })
  .then(res => {
    if (!res.ok) return res.json().then(e => { throw new Error(e.error); });
    return res.json();
  })
  .then(() => {
    showToast("Task deleted successfully.", true);
    loadDashboardData();
  })
  .catch(err => {
    showToast(err.message || "Delete task failed.", false);
  });
};

window.removeAssignment = function(id) {
  if (!confirm("Are you sure you want to remove this task assignment?")) return;

  fetch(`${API_BASE_URL}/assignments/${id}`, {
    method: "DELETE",
    credentials: "include"
  })
  .then(res => {
    if (!res.ok) return res.json().then(e => { throw new Error(e.error); });
    return res.json();
  })
  .then(() => {
    showToast("Assignment removed.", true);
    loadDashboardData();
  })
  .catch(err => {
    showToast(err.message || "Removal failed.", false);
  });
};

// ==========================================================================
// Helpers
// ==========================================================================

function showToast(message, isSuccess) {
  elements.toastMessage.textContent = message;
  
  // Set class based on success
  elements.toastContainer.className = `toast align-items-center text-white border-0 ${isSuccess ? 'bg-success' : 'bg-danger'}`;
  
  elements.toast.show();
}

function escapeHTML(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}

window.selectTaskForManagement = function(id) {
  const task = tasks.find(t => t.id === id);
  if (!task) return;

  // Set selected task in form
  elements.assignTaskSelect.value = task.id;
  elements.displayTaskId.textContent = task.id;

  // Visual pulse indicator on target box (HCI feedback heuristic)
  const panel = elements.assignmentForm.closest('.dashboard-section');
  if (panel) {
    panel.style.transition = 'outline 0.15s ease-in-out, transform 0.15s ease-in-out';
    panel.style.outline = '3px solid var(--secondary-color)';
    panel.style.transform = 'scale(1.02)';
    setTimeout(() => {
      panel.style.outline = 'none';
      panel.style.transform = 'scale(1)';
    }, 350);
  }

  showToast(`Selected task: "${task.title}"`, true);
};
