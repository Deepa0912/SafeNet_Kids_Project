import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'
import PasswordModal from '../components/PasswordModal'

export default function HomePage() {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [busy, setBusy] = useState(false)
    const [modal, setModal] = useState({ open: false, action: null, label: '' })

    const load = useCallback(async () => {
        setLoading(true)
        const { ok, data } = await api.stats()
        if (ok) setStats(data)
        setLoading(false)
    }, [])

    useEffect(() => { load() }, [load])

    const confirmToggleMonitor = (start) => {
        setModal({
            open: true,
            label: start ? 'start monitoring' : 'stop monitoring',
            action: () => toggleMonitor(start)
        })
    }

    const toggleMonitor = async (start) => {
        setModal({ open: false, action: null, label: '' })
        setBusy(true)
        if (start) await api.startMonitor()
        else await api.stopMonitor()
        await load()
        setBusy(false)
    }

    const riskClass = !stats ? '' : stats.risk_score <= 30 ? 'risk-low' : stats.risk_score <= 70 ? 'risk-medium' : 'risk-high'
    const cats = stats?.category_counts ?? {}
    const catKeys = Object.keys(cats)
    const max = catKeys.length ? Math.max(...catKeys.map(k => cats[k])) : 1

    return (
        <div className="page">
            <div className="page-header">
                <h1>Control Center</h1>
                <p className="page-desc">Real-time child safety overview</p>
            </div>

            {loading ? <p className="loading">Loading stats…</p> : stats ? <>
                {/* Stat cards */}
                <div className="stat-grid">
                    <div className={`stat-card ${riskClass}`}>
                        <div className="stat-label">Risk Score</div>
                        <div className="stat-value">{stats.risk_score}</div>
                        <div className="stat-badge">{stats.risk_label}</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Total Threats (7d)</div>
                        <div className="stat-value">{stats.total_threats}</div>
                        <div className="stat-badge">Last 7 days</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Monitor Status</div>
                        <div className="stat-value status-dot-wrap">
                            <span className={`status-dot ${stats.monitor_running ? 'on' : 'off'}`} />
                        </div>
                        <div className="stat-badge">{stats.monitor_running ? 'Active' : 'Stopped'}</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Blocked Sites</div>
                        <div className="stat-value">{stats.blocked_sites_count}</div>
                        <div className="stat-badge">Configured</div>
                    </div>
                </div>

                {/* Monitor controls */}
                <div className="card">
                    <h3>Monitor Controls</h3>
                    <div className="controls-row">
                        <button className="btn-success" disabled={busy || stats.monitor_running} onClick={() => confirmToggleMonitor(true)}>▶ Start Monitoring</button>
                        <button className="btn-danger" disabled={busy || !stats.monitor_running} onClick={() => confirmToggleMonitor(false)}>⏹ Stop Monitoring</button>
                        <button className="btn-secondary" onClick={load}>🔄 Refresh Stats</button>
                    </div>
                </div>

                {/* Threat breakdown */}
                <div className="card">
                    <h3>Threat Breakdown (Last 7 Days)</h3>
                    {catKeys.length === 0
                        ? <p className="muted">No threats detected in the last 7 days. ✅</p>
                        : <div className="threat-breakdown">
                            {catKeys.map(cat => (
                                <div key={cat} className="threat-row">
                                    <span className="threat-row-label">{cat}</span>
                                    <div className="threat-bar-bg">
                                        <div className="threat-bar-fill" style={{ width: `${(cats[cat] / max) * 100}%` }} />
                                    </div>
                                    <span className="threat-count">{cats[cat]}</span>
                                </div>
                            ))}
                        </div>
                    }
                </div>
            </> : <p className="muted">Could not load stats.</p>}

            <PasswordModal
                isOpen={modal.open}
                onClose={() => setModal({ open: false, action: null, label: '' })}
                onVerified={modal.action}
                actionLabel={modal.label}
            />
        </div>
    )
}
