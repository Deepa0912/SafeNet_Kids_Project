import { useState, useEffect } from 'react'
import { api } from '../api'
import PasswordModal from '../components/PasswordModal'

export default function DatabasePage() {
    const [sites, setSites] = useState([])
    const [cats, setCats] = useState({})
    const [newSite, setNewSite] = useState('')
    const [loading, setLoading] = useState(true)
    const [modal, setModal] = useState({ open: false, action: null, label: '' })

    const load = async () => {
        setLoading(true)
        const { ok, data } = await api.database()
        if (ok) { setSites(data.blocked_sites || []); setCats(data.categories || {}) }
        setLoading(false)
    }

    useEffect(() => { load() }, [])

    const confirmAddSite = (e) => {
        e.preventDefault()
        if (!newSite.trim()) return
        setModal({
            open: true,
            label: `block ${newSite.trim()}`,
            action: async () => {
                setModal({ open: false, action: null, label: '' })
                const { ok, data } = await api.addBlockedSite(newSite.trim())
                if (ok) { setSites(data.blocked_sites || []); setNewSite('') }
            }
        })
    }

    const confirmRemoveSite = (site) => {
        setModal({
            open: true,
            label: `unblock ${site}`,
            action: async () => {
                setModal({ open: false, action: null, label: '' })
                const { ok, data } = await api.removeBlockedSite(site)
                if (ok) setSites(data.blocked_sites || [])
            }
        })
    }

    if (loading) return <div className="page"><p className="loading">Loading database…</p></div>

    return (
        <div className="page">
            <div className="page-header">
                <h1>Threat Database</h1>
                <p className="page-desc">Manage blocked websites and keyword categories</p>
            </div>

            {/* Blocked sites */}
            <div className="card">
                <h3>Blocked Websites</h3>
                <form className="add-row" onSubmit={confirmAddSite}>
                    <input value={newSite} onChange={e => setNewSite(e.target.value)} placeholder="e.g. example.com" />
                    <button type="submit" className="btn-primary btn-sm">+ Add Site</button>
                </form>
                <div className="tag-list">
                    {sites.length === 0
                        ? <p className="muted">No blocked sites configured.</p>
                        : sites.map(site => (
                            <div key={site} className="tag">
                                <span>{site}</span>
                                <span className="tag-del" onClick={() => confirmRemoveSite(site)}>✕</span>
                            </div>
                        ))
                    }
                </div>
            </div>

            {/* Keyword categories */}
            <div className="card">
                <h3>Keyword Categories</h3>
                {Object.keys(cats).length === 0
                    ? <p className="muted">No keyword categories configured.</p>
                    : <div className="categories-grid">
                        {Object.entries(cats).map(([name, words]) => (
                            <div key={name} className="category-card">
                                <div className="category-name">{name}</div>
                                <div className="keyword-chips">
                                    {(words || []).map(w => <span key={w} className="keyword-chip">{w}</span>)}
                                </div>
                            </div>
                        ))}
                    </div>
                }
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
