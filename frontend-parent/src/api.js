// api.js — All API calls to FastAPI backend
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Attach JWT token from localStorage to every request
api.interceptors.request.use(cfg => {
    const token = localStorage.getItem('token')
    if (token) cfg.headers.Authorization = `Bearer ${token}`
    return cfg
})

export default api

// ── Auth ───────────────────────────────────────────────────────────
export const authAPI = {
    login: (username, password) =>
        api.post('/auth/login', new URLSearchParams({ username, password }), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }),
    register: (username, password, email) =>
        api.post('/auth/register', { username, password, email }),
    reset: (username, newPassword) =>
        api.post('/auth/reset-password', { username, new_password: newPassword }),
}

// ── Parent ─────────────────────────────────────────────────────────
export const parentAPI = {
    getChildren: () => api.get('/parent/children'),
    addChild: (name) => api.post('/parent/children', { name }),
    getDashboard: (childId) => api.get(`/parent/dashboard/${childId}`),
    getThreats: (childId) => api.get(`/parent/threats/${childId}`),
    getScreenshots: (childId) => api.get(`/parent/screenshots/${childId}`),
    getBlockedSites: () => api.get('/parent/blocked-sites'),
    addBlockedSite: (url, cid) => api.post('/parent/blocked-sites', { url, child_id: cid }),
    removeBlockedSite: (id) => api.delete(`/parent/blocked-sites/${id}`),
    getBlockedApps: () => api.get('/parent/blocked-apps'),
    addBlockedApp: (appName, cid) => api.post('/parent/blocked-apps', { app_name: appName, child_id: cid }),
    removeBlockedApp: (id) => api.delete(`/parent/blocked-apps/${id}`),
    controlDevice: (childId, action) => api.post(`/parent/control/${childId}`, { action }),
    getNotifications: () => api.get('/parent/notifications'),
    markRead: (id) => api.patch(`/parent/notifications/${id}/read`),
    downloadReport: async (childId, period = 'weekly') => {
        const res = await api.get(`/reports/${childId}?period=${period}`, { responseType: 'blob' })
        const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
        const a = document.createElement('a')
        a.href = url
        a.download = `safenet_report_${period}.pdf`
        a.click()
        URL.revokeObjectURL(url)
    },
    getEmailSettings: () => api.get('/parent/email-settings'),
    saveEmailSettings: (data) => api.put('/parent/email-settings', data),
    getAISummary: (childId) => api.get(`/parent/ai-summary/${childId}`),
    getScreentimeStats: (childId) => api.get(`/parent/screentime-stats/${childId}`),
    changePassword: (data) => api.put('/parent/change-password', data),
}
