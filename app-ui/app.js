// Base API configuration — points at the deployed backend.
const API_BASE_URL = 'https://clonefest-2.onrender.com';

// Hardcoded for now — swap once there's a project picker in the UI.
// (Matches the seeded "BugOff Demo" project, key BO, id 1.)
const CURRENT_PROJECT_ID = 1;

// DOM Elements
const authView = document.getElementById('auth-view');
const dashboardView = document.getElementById('dashboard-view');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const userDisplay = document.getElementById('user-display');
const logoutBtn = document.getElementById('logout-btn');
const bugTableBody = document.getElementById('bug-table-body');

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
      detail = data.detail || detail;
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
    <tr><td colspan="5" class="px-6 py-8 text-center text-slate-500">Loading bugs…</td></tr>
  `;

  try {
    const [bugs, stats] = await Promise.all([
      apiRequest(`/bugs?project_id=${CURRENT_PROJECT_ID}`),
      apiRequest(`/projects/${CURRENT_PROJECT_ID}/stats`),
    ]);

    renderStats(stats);
    renderBugTable(bugs);
  } catch (err) {
    bugTableBody.innerHTML = `
      <tr><td colspan="5" class="px-6 py-8 text-center text-red-400">${escapeHtml(err.message)}</td></tr>
    `;
  }
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
      throw new Error(data.detail || 'Invalid username or password');
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

// Initial run
checkAuth();