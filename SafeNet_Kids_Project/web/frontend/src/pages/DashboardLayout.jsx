import { useState } from 'react'
import { api } from '../api'
import HomePage from './HomePage'
import MonitorPage from './MonitorPage'
import LogsPage from './LogsPage'
import DatabasePage from './DatabasePage'
import AppsPage from './AppsPage'

const NAV = [
    { id: 'home', icon: '🏠', label: 'Home' },
    { id: 'monitor', icon: '🔍', label: 'Threat Monitor' },
    { id: 'logs', icon: '📋', label: 'Activity Logs' },
    { id: 'database', icon: '🗄️', label: 'Database' },
    { id: 'apps', icon: '🚫', label: 'Blocked Apps' },
]

export default function DashboardLayout({ user, onLogout }) {
    const [page, setPage] = useState('home')

    const handleLogout = async () => {
        await api.logout()
        onLogout()
    }

    const renderPage = () => {
        switch (page) {
            case 'home': return <HomePage />
            case 'monitor': return <MonitorPage />
            case 'logs': return <LogsPage />
            case 'database': return <DatabasePage />
            case 'apps': return <AppsPage />
            default: return <HomePage />
        }
    }

    return (
        <div className="app-shell">
            <nav className="sidebar">
                <div className="sidebar-logo">
                    <div className="logo-icon">🛡️</div>
                    <div className="logo-text">
                        <span className="logo-main">SafeNet</span>
                        <span className="logo-sub accent">Kids</span>
                    </div>
                </div>
                <ul className="nav-list">
                    {NAV.map(n => (
                        <li key={n.id}
                            className={`nav-item ${page === n.id ? 'active' : ''}`}
                            onClick={() => setPage(n.id)}>
                            <span className="nav-icon">{n.icon}</span>
                            <span>{n.label}</span>
                        </li>
                    ))}
                </ul>
                <div className="sidebar-footer">
                    <div className="user-pill">
                        <div className="user-avatar">👤</div>
                        <div className="user-info">
                            <span className="user-name">{user.display_name || user.username}</span>
                            <span className="user-role">Parent Admin</span>
                        </div>
                    </div>
                    <button className="btn-logout" title="Sign out" onClick={handleLogout}>⏻</button>
                </div>
            </nav>

            <main className="content">
                {renderPage()}
            </main>
        </div>
    )
}
