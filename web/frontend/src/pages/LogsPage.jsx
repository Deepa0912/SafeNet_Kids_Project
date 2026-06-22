import { useState, useEffect } from 'react'
import { api } from '../api'

export default function LogsPage() {
    const [entries, setEntries] = useState(null)

    const load = async () => {
        setEntries(null)
        const { ok, data } = await api.logs(500)
        setEntries(ok && Array.isArray(data) ? data : [])
    }

    useEffect(() => { load() }, [])

    return (
        <div className="page">
            <div className="page-header">
                <h1>Activity Logs</h1>
                <p className="page-desc">Full audit trail of system events</p>
            </div>
            <div className="card">
                <div className="card-toolbar">
                    <span>All Log Events {entries && `(${entries.length})`}</span>
                    <button className="btn-secondary btn-sm" onClick={load}>🔄 Refresh</button>
                </div>
                {!entries
                    ? <p className="loading">Loading…</p>
                    : entries.length === 0
                        ? <p className="muted center">No log entries found.</p>
                        : <div className="log-table-wrap">
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
                }
            </div>
        </div>
    )
}
