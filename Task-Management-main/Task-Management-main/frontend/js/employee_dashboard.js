/**
 * Employee Dashboard Module
 * Custom JavaScript (Vanilla ES6)
 */

const API_BASE_URL = (window.location.protocol === "file:")
  ? "http://127.0.0.1:5000/api"
  : window.location.origin + "/api";

let currentUser = null;
let myAssignments = [];

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
    welcomeMessage: document.getElementById("welcomeMessage"),
    
    // Metrics
    metricMyTotalTasks: document.getElementById("metricMyTotalTasks"),
    metricMyPendingTasks: document.getElementById("metricMyPendingTasks"),
    metricMyCompletedTasks: document.getElementById("metricMyCompletedTasks"),
    
    // Table
    myAssignmentsTableBody: document.getElementById("myAssignmentsTableBody"),
    
    // Modal
    statusModal: new bootstrap.Modal(document.getElementById("statusModal")),
    statusForm: document.getElementById("statusForm"),
    modalAssignmentId: document.getElementById("modalAssignmentId"),
    statusSelect: document.getElementById("statusSelect"),
    completionRange: document.getElementById("completionRange"),
    completionValue: document.getElementById("completionValue"),
    remarksInput: document.getElementById("remarksInput"),
    
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
    if (user.role !== "employee") {
      // Admins are directed to admin dashboard
      window.location.href = "dashboard.html";
      return;
    }
    currentUser = user;
    elements.currentUserName.textContent = user.username;
    elements.currentUserRole.textContent = "Employee";
    elements.welcomeMessage.textContent = `Welcome back, ${user.username}!`;
    loadAssignments();
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

  // Sync completion percentage range output
  elements.completionRange.addEventListener("input", (e) => {
    elements.completionValue.textContent = `${e.target.value}%`;
  });

  // Form Submit for status/progress update
  elements.statusForm.addEventListener("submit", handleStatusSubmit);
}

function loadAssignments() {
  if (!currentUser || !currentUser.employee_id) {
    showToast("Employee profile not linked to user account.", false);
    return;
  }

  fetch(`${API_BASE_URL}/assignments/employee/${currentUser.employee_id}`, { credentials: "include" })
    .then(res => {
      if (!res.ok) throw new Error("Failed to load assignments.");
      return res.json();
    })
    .then(data => {
      myAssignments = data;
      renderAssignments();
      updateMetrics();
    })
    .catch(err => {
      showToast(err.message, false);
    });
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
// Render & UI Functions
// ==========================================================================

function renderAssignments() {
  const tbody = elements.myAssignmentsTableBody;
  if (myAssignments.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">You have no tasks assigned currently!</td></tr>`;
    return;
  }

  tbody.innerHTML = myAssignments.map(a => `
    <tr>
      <td>
        <div class="fw-bold">${escapeHTML(a.task_title)}</div>
        <div class="small text-muted text-truncate" style="max-width: 250px;">${escapeHTML(a.task_description || 'No description')}</div>
      </td>
      <td><span class="badge-status ${a.task_priority.toLowerCase()}">${a.task_priority}</span></td>
      <td>${a.deadline ? formatDate(a.deadline) : 'No deadline'}</td>
      <td>
        <div class="d-flex align-items-center">
          <div class="progress flex-grow-1 me-2" style="height: 6px;">
            <div class="progress-bar bg-primary" role="progressbar" style="width: ${a.completion_percentage}%" aria-valuenow="${a.completion_percentage}" aria-valuemin="0" aria-valuemax="100"></div>
          </div>
          <span class="small fw-bold text-muted">${a.completion_percentage}%</span>
        </div>
      </td>
      <td><span class="badge-status ${a.status.toLowerCase().replace(" ", "-")}">${a.status}</span></td>
      <td>
        <button class="btn btn-sm btn-outline-primary" onclick="openUpdateStatusModal(${a.id})">
          <i class="bi bi-pencil-square me-1"></i> Update
        </button>
      </td>
    </tr>
  `).join("");
}

function updateMetrics() {
  elements.metricMyTotalTasks.textContent = myAssignments.length;
  
  const inProgressCount = myAssignments.filter(a => a.status === "In Progress").length;
  elements.metricMyPendingTasks.textContent = inProgressCount;
  
  const completedCount = myAssignments.filter(a => a.status === "Completed").length;
  elements.metricMyCompletedTasks.textContent = completedCount;
}

// ==========================================================================
// Progress Actions
// ==========================================================================

window.openUpdateStatusModal = function(id) {
  const assignment = myAssignments.find(a => a.id === id);
  if (!assignment) return;

  elements.modalAssignmentId.value = assignment.id;
  elements.statusSelect.value = assignment.status;
  elements.completionRange.value = assignment.completion_percentage;
  elements.completionValue.textContent = `${assignment.completion_percentage}%`;
  elements.remarksInput.value = assignment.remarks || "";

  elements.statusModal.show();
};

function handleStatusSubmit(e) {
  e.preventDefault();

  const id = elements.modalAssignmentId.value;
  const statusData = {
    status: elements.statusSelect.value,
    completion_percentage: parseInt(elements.completionRange.value),
    remarks: elements.remarksInput.value.trim()
  };

  fetch(`${API_BASE_URL}/assignments/${id}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(statusData),
    credentials: "include"
  })
  .then(res => {
    if (!res.ok) return res.json().then(e => { throw new Error(e.error); });
    return res.json();
  })
  .then(() => {
    elements.statusModal.hide();
    showToast("Task assignment progress updated successfully.", true);
    loadAssignments();
  })
  .catch(err => {
    showToast(err.message || "Failed to update progress.", false);
  });
}

// ==========================================================================
// Helpers
// ==========================================================================

function showToast(message, isSuccess) {
  elements.toastMessage.textContent = message;
  elements.toastContainer.className = `toast align-items-center text-white border-0 ${isSuccess ? 'bg-success' : 'bg-danger'}`;
  elements.toast.show();
}

function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
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
