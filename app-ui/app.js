// Base API configuration — points at the deployed backend.
const API_BASE_URL = 'https://clonefest-2.onrender.com';

// Set once loadDashboard() discovers which project the logged-in user
// actually belongs to — no longer hardcoded, since judges/new users
// create their own project rather than being invited to a fixed one.
let currentProjectId = null;

// Turns a FastAPI error response's `detail` (string, or a list of
// Pydantic validation error objects) into one readable string.
function formatApiError(data, fallback) {
  if (!data || !data.detail) return fallback;
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((e) => {
        const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : '';
        return field ? `${field}: ${e.msg}` : e.msg;
      })
      .join('; ');
  }
  return fallback;
}

// DOM Elements
const authView = document.getElementById('auth-view');
const dashboardView = document.getElementById('dashboard-view');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const signupForm = document.getElementById('signup-form');
const signupError = document.getElementById('signup-error');
const signupSuccess = document.getElementById('signup-success');
const showSignupLink = document.getElementById('show-signup');
const showLoginLink = document.getElementById('show-login');
const authSubtitle = document.getElementById('auth-subtitle');
const userDisplay = document.getElementById('user-display');
const logoutBtn = document.getElementById('logout-btn');
const bugTableBody = document.getElementById('bug-table-body');
const newBugBtn = document.getElementById('new-bug-btn');
const newBugModal = document.getElementById('new-bug-modal');
const newBugClose = document.getElementById('new-bug-close');
const newBugForm = document.getElementById('new-bug-form');
const newBugError = document.getElementById('new-bug-error');
const newProjectModal = document.getElementById('new-project-modal');
const newProjectClose = document.getElementById('new-project-close');
const newProjectForm = document.getElementById('new-project-form');
const newProjectError = document.getElementById('new-project-error');

// ---------------------------------------------------------------
// API client — every authenticated call goes through this so the
// token attachment and 401 handling only live in one place.
// ---------------------------------------------------------------
async function apiRequest(path, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = {
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (response.status === 401) {
    // Token missing/expired/invalid — force back to login rather than
    // showing a broken dashboard.
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    checkAuth();
    throw new Error('Session expired — please sign in again.');
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const data = await response.json();
      detail = formatApiError(data, detail);
    } catch (_) {
      /* body wasn't JSON — keep the generic message */
    }
    throw new Error(detail);
  }

  // 204 No Content etc. — nothing to parse.
  if (response.status === 204) return null;
  return response.json();
}

// ---------------------------------------------------------------
// Dashboard data
// ---------------------------------------------------------------
const SEVERITY_STYLES = {
  critical: 'bg-red-950 text-red-400 border-red-800',
  high: 'bg-red-950 text-red-400 border-red-800',
  medium: 'bg-amber-950 text-amber-400 border-amber-800',
  low: 'bg-slate-800 text-slate-400 border-slate-700',
  trivial: 'bg-slate-800 text-slate-400 border-slate-700',
};

const STATUS_STYLES = {
  new: 'bg-slate-800 text-slate-300 border-slate-700',
  confirmed: 'bg-amber-950 text-amber-400 border-amber-800',
  in_progress: 'bg-amber-950 text-amber-400 border-amber-800',
  resolved: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  verified: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  closed: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  reopened: 'bg-red-950 text-red-400 border-red-800',
};

function badge(text, styleMap, key) {
  const cls = styleMap[key] || 'bg-slate-800 text-slate-400 border-slate-700';
  return `<span class="px-2 py-1 text-xs rounded-md border ${cls}">${text}</span>`;
}

function renderBugRow(bug) {
  const severityLabel = bug.severity.charAt(0).toUpperCase() + bug.severity.slice(1);
  const statusLabel = bug.status.replace('_', ' ');
  return `
    <tr class="hover:bg-slate-800/30">
      <td class="px-6 py-4 font-mono text-xs text-indigo-400">BUG-${bug.id}</td>
      <td class="px-6 py-4 font-medium text-white">${escapeHtml(bug.title)}</td>
      <td class="px-6 py-4">${badge(severityLabel, SEVERITY_STYLES, bug.severity)}</td>
      <td class="px-6 py-4 text-slate-400">${bug.component_name || '—'}</td>
      <td class="px-6 py-4">${badge(statusLabel, STATUS_STYLES, bug.status)}</td>
    </tr>
  `;
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

async function loadDashboard() {
  bugTableBody.innerHTML = `
    <tr><td colspan="5" class="px-6 py-8 text-center text-slate-500">Loading…</td></tr>
  `;

  try {
    const projects = await apiRequest('/projects');

    if (!Array.isArray(projects) || projects.length === 0) {
      showNoProjectState();
      return;
    }

    // Use their first project. (Multi-project support / a picker is a
    // natural next step, but every user always has at least one project
    // now that project creation auto-assigns them as admin.)
    currentProjectId = projects[0].id;
    document.getElementById('project-name').textContent = projects[0].name;

    const [bugs, stats] = await Promise.all([
      apiRequest(`/bugs?project_id=${currentProjectId}`),
      apiRequest(`/projects/${currentProjectId}/stats`),
    ]);

    renderStats(stats);
    renderBugTable(bugs);
  } catch (err) {
    bugTableBody.innerHTML = `
      <tr><td colspan="5" class="px-6 py-8 text-center text-red-400">${escapeHtml(err.message)}</td></tr>
    `;
  }
}

function showNoProjectState() {
  document.getElementById('project-name').textContent = 'No project yet';
  document.getElementById('stat-total').textContent = '— Issues';
  document.getElementById('stat-critical').textContent = '— Critical';
  document.getElementById('stat-resolved').textContent = '— Closed';
  bugTableBody.innerHTML = `
    <tr><td colspan="5" class="px-6 py-10 text-center text-slate-400">
      You're not part of a project yet.<br />
      <button id="empty-state-create-btn" class="mt-4 bg-indigo-600 hover:bg-indigo-500 text-xs px-4 py-2 rounded-lg font-medium transition">
        + Create Your First Project
      </button>
    </td></tr>
  `;
  document.getElementById('empty-state-create-btn').addEventListener('click', () => {
    newProjectModal.classList.remove('hidden');
  });
}

function renderBugTable(bugs) {
  if (!Array.isArray(bugs) || bugs.length === 0) {
    bugTableBody.innerHTML = `
      <tr><td colspan="5" class="px-6 py-8 text-center text-slate-500">No bugs yet for this project.</td></tr>
    `;
    return;
  }
  bugTableBody.innerHTML = bugs.map(renderBugRow).join('');
}

function renderStats(stats) {
  // Confirmed shape from GET /projects/{id}/stats:
  // { total_bugs, open_bugs, closed_bugs, by_status, by_severity,
  //   by_priority, by_component, by_assignee }
  const totalEl = document.getElementById('stat-total');
  const criticalEl = document.getElementById('stat-critical');
  const resolvedEl = document.getElementById('stat-resolved');

  if (totalEl) totalEl.textContent = `${stats.total_bugs ?? '—'} Issues`;
  if (criticalEl) {
    const critical = stats.by_severity?.critical ?? 0;
    criticalEl.textContent = `${critical} Critical`;
  }
  if (resolvedEl) resolvedEl.textContent = `${stats.closed_bugs ?? '—'} Closed`;
}

// ---------------------------------------------------------------
// New bug modal
// ---------------------------------------------------------------
newBugBtn.addEventListener('click', () => {
  newBugError.classList.add('hidden');
  newBugForm.reset();
  newBugModal.classList.remove('hidden');
});

newBugClose.addEventListener('click', () => {
  newBugModal.classList.add('hidden');
});

newBugModal.addEventListener('click', (e) => {
  // Click on the dark backdrop (not the card itself) closes the modal.
  if (e.target === newBugModal) newBugModal.classList.add('hidden');
});

newBugForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  newBugError.classList.add('hidden');

  const title = document.getElementById('bug-title').value.trim();
  const description = document.getElementById('bug-description').value.trim();
  const severity = document.getElementById('bug-severity').value;
  const priority = document.getElementById('bug-priority').value;

  const submitBtn = document.getElementById('new-bug-submit');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting…';

  try {
    await apiRequest(`/bugs?project_id=${currentProjectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        description,
        severity,
        priority,
      }),
    });

    newBugModal.classList.add('hidden');
    loadDashboard();
  } catch (err) {
    newBugError.textContent = err.message;
    newBugError.classList.remove('hidden');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Bug';
  }
});

newProjectClose.addEventListener('click', () => {
  newProjectModal.classList.add('hidden');
});

newProjectModal.addEventListener('click', (e) => {
  if (e.target === newProjectModal) newProjectModal.classList.add('hidden');
});

newProjectForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  newProjectError.classList.add('hidden');

  const name = document.getElementById('project-name-input').value.trim();
  const key = document.getElementById('project-key-input').value.trim().toUpperCase();
  const description = document.getElementById('project-description-input').value.trim();

  const submitBtn = document.getElementById('new-project-submit');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Creating…';

  try {
    await apiRequest('/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, key, description }),
    });

    newProjectModal.classList.add('hidden');
    newProjectForm.reset();
    loadDashboard();
  } catch (err) {
    newProjectError.textContent = err.message;
    newProjectError.classList.remove('hidden');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Create Project';
  }
});

// ---------------------------------------------------------------
// Auth
// ---------------------------------------------------------------
function checkAuth() {
  const token = localStorage.getItem('access_token');
  const user = localStorage.getItem('username');

  if (token) {
    authView.classList.add('hidden');
    dashboardView.classList.remove('hidden');
    userDisplay.textContent = user ? `Logged in as: ${user}` : 'Authenticated';
    loadDashboard();
  } else {
    authView.classList.remove('hidden');
    dashboardView.classList.add('hidden');
  }
}

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.classList.add('hidden');

  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();

  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(formatApiError(data, 'Invalid username or password'));
    }

    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('username', username);
    checkAuth();
  } catch (err) {
    loginError.textContent = err.message || 'Failed to connect to authentication server.';
    loginError.classList.remove('hidden');
  }
});

logoutBtn.addEventListener('click', () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('username');
  checkAuth();
});

// ---------------------------------------------------------------
// Signup / login toggle
// ---------------------------------------------------------------
showSignupLink.addEventListener('click', (e) => {
  e.preventDefault();
  loginForm.classList.add('hidden');
  signupForm.classList.remove('hidden');
  showSignupLink.classList.add('hidden');
  showLoginLink.classList.remove('hidden');
  authSubtitle.textContent = 'Create an account to get started';
  loginError.classList.add('hidden');
  signupError.classList.add('hidden');
  signupSuccess.classList.add('hidden');
});

showLoginLink.addEventListener('click', (e) => {
  e.preventDefault();
  signupForm.classList.add('hidden');
  loginForm.classList.remove('hidden');
  showLoginLink.classList.add('hidden');
  showSignupLink.classList.remove('hidden');
  authSubtitle.textContent = 'Sign in to access your bug tracking dashboard';
  loginError.classList.add('hidden');
  signupError.classList.add('hidden');
  signupSuccess.classList.add('hidden');
});

signupForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  signupError.classList.add('hidden');
  signupSuccess.classList.add('hidden');

  const username = document.getElementById('signup-username').value.trim();
  const email = document.getElementById('signup-email').value.trim();
  const fullName = document.getElementById('signup-fullname').value.trim();
  const password = document.getElementById('signup-password').value.trim();

  try {
    const registerResponse = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username,
        email,
        password,
        full_name: fullName || undefined,
      }),
    });

    const registerData = await registerResponse.json();

    if (!registerResponse.ok) {
      throw new Error(formatApiError(registerData, 'Could not create account'));
    }

    // Auto-login right after successful signup so the person lands
    // straight on the dashboard instead of having to type creds twice.
    const loginFormData = new URLSearchParams();
    loginFormData.append('username', username);
    loginFormData.append('password', password);

    const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: loginFormData.toString(),
    });

    const loginData = await loginResponse.json();

    if (!loginResponse.ok) {
      // Account was created but auto-login failed for some reason —
      // send them to the login form instead of leaving them stuck.
      signupSuccess.textContent = 'Account created — please sign in.';
      signupSuccess.classList.remove('hidden');
      showLoginLink.click();
      return;
    }

    localStorage.setItem('access_token', loginData.access_token);
    localStorage.setItem('username', username);
    checkAuth();
  } catch (err) {
    signupError.textContent = err.message || 'Failed to create account.';
    signupError.classList.remove('hidden');
  }
});

// Initial run
checkAuth();