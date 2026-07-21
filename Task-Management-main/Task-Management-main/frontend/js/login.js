/* ==========================================================================
   Task Management System - Login Module
   Custom JavaScript (Vanilla ES6)

   NOTE: This is Phase 1 (Frontend Only). All authentication below is
   SIMULATED using hard-coded credentials and localStorage. When the Flask
   backend is ready, replace the body of fakeAuthentication() with a real
   fetch() call to the Flask login API (see README.md for the plan).
   ========================================================================== */

// --------------------------------------------------------------------------
const API_BASE_URL = (window.location.protocol === "file:")
  ? "http://127.0.0.1:5000/api"
  : window.location.origin + "/api";

// --------------------------------------------------------------------------
// DOM element references (populated on DOMContentLoaded)
// --------------------------------------------------------------------------
let elements = {};

/**
 * Entry point. Runs once the DOM is fully loaded.
 */
document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  initializeLogin();
});

/**
 * Cache all DOM elements used throughout the module so we only
 * query the DOM once.
 */
function cacheElements() {
  elements = {
    form: document.getElementById("loginForm"),
    username: document.getElementById("username"),
    password: document.getElementById("password"),
    usernameError: document.getElementById("usernameError"),
    passwordError: document.getElementById("passwordError"),
    showPassword: document.getElementById("showPassword"),
    rememberMe: document.getElementById("rememberMe"),
    loginBtn: document.getElementById("loginBtn"),
    loginBtnText: document.getElementById("loginBtnText"),
    loginSpinner: document.getElementById("loginSpinner"),
    loginAlert: document.getElementById("loginAlert"),
  };
}

/**
 * Set up the login page: check for an existing session, wire up
 * event listeners, and focus the username field.
 */
function initializeLogin() {
  // If the user is already logged in, skip the login form entirely.
  // checkExistingLogin();

  // Focus username field for accessibility / convenience.
  if (elements.username) {
    elements.username.focus();
  }

  // Form submit handler (covers both button click and Enter key).
  elements.form.addEventListener("submit", handleFormSubmit);

  // Show/hide password toggle.
  elements.showPassword.addEventListener("change", togglePassword);

  // Live validation feedback as the user types.
  elements.username.addEventListener("input", () => validateField("username"));
  elements.password.addEventListener("input", () => validateField("password"));
}

/**
 * Checks localStorage for an existing session. If a valid session is
 * found, the user is redirected immediately based on their role.
 */
function checkExistingLogin() {
  fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      "Accept": "application/json"
    },
    credentials: "include"
  })
  .then((response) => {
    if (response.ok) {
      return response.json();
    }
    throw new Error("Not logged in");
  })
  .then((user) => {
    saveSession(user);
    redirectUser(user.role);
  })
  .catch(() => {
    // If not authenticated, clear any stale session info
    localStorage.removeItem("loggedIn");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
  });
}

/**
 * Handles the form submission event: prevents default browser
 * submission, runs validation, and triggers fake authentication
 * if the form is valid.
 * @param {SubmitEvent} event
 */
function handleFormSubmit(event) {
  event.preventDefault();
  hideAlert();

  const isValid = validateForm();

  if (!isValid) {
    return;
  }

  const username = elements.username.value.trim();
  const password = elements.password.value;

  setLoadingState(true);

  authenticateUser(username, password)
    .then((user) => {
      saveSession(user);
      redirectUser(user.role);
    })
    .catch((error) => {
      setLoadingState(false);
      showAlert(error.message || "Invalid username or password.");
    });
}

/**
 * Validates the entire form (username + password fields).
 * @returns {boolean} true if both fields pass validation.
 */
function validateForm() {
  const isUsernameValid = validateField("username");
  const isPasswordValid = validateField("password");
  return isUsernameValid && isPasswordValid;
}

/**
 * Validates a single field ("username" or "password") and applies
 * Bootstrap's is-valid / is-invalid classes accordingly.
 * @param {"username"|"password"} fieldName
 * @returns {boolean} true if the field is valid.
 */
function validateField(fieldName) {
  const field = elements[fieldName];
  const value = field.value.trim();
  let isValid = true;
  let message = "";

  if (fieldName === "username") {
    if (value.length === 0) {
      isValid = false;
      message = "Username is required.";
    } else if (value.length < 4) {
      isValid = false;
      message = "Username must be at least 4 characters.";
    }
    elements.usernameError.textContent = message;
  }

  if (fieldName === "password") {
    // Password intentionally not trimmed, spaces may be part of it.
    const pwdValue = field.value;
    if (pwdValue.length === 0) {
      isValid = false;
      message = "Password is required.";
    } else if (pwdValue.length < 6) {
      isValid = false;
      message = "Password must be at least 6 characters.";
    }
    elements.passwordError.textContent = message;
  }

  field.classList.toggle("is-invalid", !isValid);
  field.classList.toggle("is-valid", isValid);

  return isValid;
}

/**
 * Toggles the password field between "password" and "text" types
 * based on the "Show password" checkbox.
 */
function togglePassword() {
  elements.password.type = elements.showPassword.checked ? "text" : "password";
}

/**
 * Authenticates against the real Flask backend API.
 * @param {string} username
 * @param {string} password
 * @returns {Promise<{username: string, role: string}>}
 */
function authenticateUser(username, password) {
  return fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    credentials: "include",
    body: JSON.stringify({ username, password })
  })
  .then((response) => {
    if (!response.ok) {
      return response.json().then((err) => {
        throw new Error(err.error || "Invalid username or password.");
      });
    }
    return response.json();
  });
}

/**
 * Persists session details in localStorage.
 * @param {{username: string, role: string}} user
 */
function saveSession(user) {
  localStorage.setItem("loggedIn", "true");
  localStorage.setItem("username", user.username);
  localStorage.setItem("role", user.role);
  localStorage.setItem("loginTime", new Date().toISOString());
}

/**
 * Redirects the user to the correct dashboard page based on role.
 * @param {"admin"|"employee"} role
 */
function redirectUser(role) {
  if (role === "admin") {
    window.location.href = "dashboard.html";
  } else if (role === "employee") {
    window.location.href = "employee_dashboard.html";
  }
}

/**
 * Displays a Bootstrap alert with the given message.
 * @param {string} message
 */
function showAlert(message) {
  elements.loginAlert.textContent = message;
  elements.loginAlert.classList.remove("d-none");
}

/**
 * Hides the login alert box.
 */
function hideAlert() {
  elements.loginAlert.classList.add("d-none");
  elements.loginAlert.textContent = "";
}

/**
 * Toggles the loading state of the login button: shows/hides the
 * spinner, updates button text, and disables the button while loading.
 * @param {boolean} isLoading
 */
function setLoadingState(isLoading) {
  elements.loginBtn.disabled = isLoading;
  elements.loginSpinner.classList.toggle("d-none", !isLoading);
  elements.loginBtnText.textContent = isLoading ? "Logging in..." : "Login";
}
