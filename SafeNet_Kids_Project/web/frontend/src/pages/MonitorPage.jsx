import { useState, useEffect } from 'react'
import { api } from '../api'

function LogTable({ entries }) {
    if (!entries) return <p className="loading">Loading…</p>
    if (!entries.length) return <p className="muted center">No entries found.</p>
    return (
        <div className="log-table-wrap">
            <table>
                <thead><tr><th>Timestamp</th><th>Level</th><th>Message</th></tr></thead>
                <tbody>
                    {entries.map((e, i) => (
                        <tr key={i}>
                            <td>{e.timestamp}</td>
                            <td className={`level-${e.level}`}>{e.level}</td>
                            <td>{e.message}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default function MonitorPage() {
    const [entries, setEntries] = useState(null)

    const load = async () => {
        setEntries(null)
        const { ok, data } = await api.logs(500)
        if (ok) {
            const threats = Array.isArray(data) ? data.filter(e =>
                e.message.includes('Threat') ||
                e.message.includes('AI Detected') ||
                e.message.includes('Panic Lock') ||
                e.message.includes('Restricted')
            ) : []
            setEntries(threats)
        } else {
            setEntries([])
        }
    }

    useEffect(() => { load() }, [])

    return (
        <div className="page">
            <div className="page-header">
                <h1>Threat Monitor</h1>
                <p className="page-desc">Live feed of detected threats only</p>
            </div>
            <div className="card">
                <div className="card-toolbar">
                    <span>Live Threat Events</span>
                    <button className="btn-secondary btn-sm" onClick={load}>🔄 Refresh</button>
                </div>
                <LogTable entries={entries} />
            </div>
        </div>
    )
}
