/* API layer — all calls to Flask backend */

const BASE = '';  // same origin in dev (proxied) and prod

async function apiFetch(path, options = {}) {
    const res = await fetch(BASE + path, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
}

export const api = {
    // Auth
    me: () => apiFetch('/api/auth/me'),
    login: (u, p) => apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify({ username: u, password: p }) }),
    register: (u, p, pp) => apiFetch('/api/auth/register', { method: 'POST', body: JSON.stringify({ username: u, password: p, parent_password: pp }) }),
    resetPassword: (u, pp, np) => apiFetch('/api/auth/reset_password', { method: 'POST', body: JSON.stringify({ username: u, parent_password: pp, new_password: np }) }),
    verifyParent: (pp) => apiFetch('/api/auth/verify_parent', { method: 'POST', body: JSON.stringify({ parent_password: pp }) }),
    logout: () => apiFetch('/api/auth/logout', { method: 'POST' }),

    // Dashboard
    stats: () => apiFetch('/api/stats'),
    logs: (limit = 200) => apiFetch(`/api/logs?limit=${limit}`),

    // Monitor
    startMonitor: () => apiFetch('/api/monitor/start', { method: 'POST' }),
    stopMonitor: () => apiFetch('/api/monitor/stop', { method: 'POST' }),

    // Database
    database: () => apiFetch('/api/database'),
    addBlockedSite: (site) => apiFetch('/api/database/blocked_sites', { method: 'POST', body: JSON.stringify({ site }) }),
    removeBlockedSite: (site) => apiFetch(`/api/database/blocked_sites/${encodeURIComponent(site)}`, { method: 'DELETE' }),

    // Blocked apps
    blockedApps: () => apiFetch('/api/blocked_apps'),
    addBlockedApp: (app) => apiFetch('/api/blocked_apps', { method: 'POST', body: JSON.stringify({ app }) }),
    removeBlockedApp: (app) => apiFetch(`/api/blocked_apps/${encodeURIComponent(app)}`, { method: 'DELETE' }),
};
