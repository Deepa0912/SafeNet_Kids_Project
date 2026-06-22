import { useState, useEffect } from 'react'
import { api } from '../api'
import PasswordModal from '../components/PasswordModal'

export default function AppsPage() {
    const [apps, setApps] = useState([])
    const [newApp, setNewApp] = useState('')
    const [loading, setLoading] = useState(true)
    const [modal, setModal] = useState({ open: false, action: null, label: '' })

    const load = async () => {
        setLoading(true)
        const { ok, data } = await api.blockedApps()
        if (ok) setApps(data.blocked_apps || [])
        setLoading(false)
    }

    useEffect(() => { load() }, [])

    const confirmAddApp = (e) => {
        e.preventDefault()
        if (!newApp.trim()) return
        setModal({
            open: true,
            label: `block ${newApp.trim()}`,
            action: async () => {
                setModal({ open: false, action: null, label: '' })
                const { ok, data } = await api.addBlockedApp(newApp.trim())
                if (ok) { setApps(data.blocked_apps || []); setNewApp('') }
            }
        })
    }

    const confirmRemoveApp = (app) => {
        setModal({
            open: true,
            label: `unblock ${app}`,
            action: async () => {
                setModal({ open: false, action: null, label: '' })
                const { ok, data } = await api.removeBlockedApp(app)
                if (ok) setApps(data.blocked_apps || [])
            }
        })
    }

    if (loading) return <div className="page"><p className="loading">Loading blocked apps…</p></div>

    return (
        <div className="page">
            <div className="page-header">
                <h1>Blocked Apps</h1>
                <p className="page-desc">Applications that will be automatically terminated</p>
            </div>
            <div className="card">
                <h3>Manage Blocked Applications</h3>
                <form className="add-row" onSubmit={confirmAddApp}>
                    <input value={newApp} onChange={e => setNewApp(e.target.value)} placeholder="e.g. chrome.exe" />
                    <button type="submit" className="btn-primary btn-sm">+ Block App</button>
                </form>
                <div className="tag-list">
                    {apps.length === 0
                        ? <p className="muted">No apps currently blocked.</p>
                        : apps.map(app => (
                            <div key={app} className="tag">
                                <span>{app}</span>
                                <span className="tag-del" onClick={() => confirmRemoveApp(app)}>✕</span>
                            </div>
                        ))
                    }
                </div>
            </div>

            <PasswordModal
                isOpen={modal.open}
                onClose={() => setModal({ open: false, action: null, label: '' })}
                onVerified={modal.action}
                actionLabel={modal.label}
            />
        </div>
    )
}
