// Base API configuration
const API_BASE_URL = window.location.origin.includes('localhost')
  ? 'http://localhost:8000'
  : '';

// DOM Elements
const authView = document.getElementById('auth-view');
const dashboardView = document.getElementById('dashboard-view');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const userDisplay = document.getElementById('user-display');
const logoutBtn = document.getElementById('logout-btn');

// Check authentication state on page load
function checkAuth() {
  const token = localStorage.getItem('access_token');
  const user = localStorage.getItem('username');

  if (token) {
    authView.classList.add('hidden');
    dashboardView.classList.remove('hidden');
    userDisplay.textContent = user ? `Logged in as: ${user}` : 'Authenticated';
  } else {
    authView.classList.remove('hidden');
    dashboardView.classList.add('hidden');
  }
}

// OAuth2 Password Grant Login handler
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.classList.add('hidden');

  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();

  // URL-encoded form data as required by OAuth2 spec
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Invalid username or password');
    }

    // Store token and switch view
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('username', username);
    checkAuth();
  } catch (err) {
    loginError.textContent = err.message || 'Failed to connect to authentication server.';
    loginError.classList.remove('hidden');
  }
});

// Logout handler
logoutBtn.addEventListener('click', () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('username');
  checkAuth();
});

// Initial run
checkAuth();