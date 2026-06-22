import { useState, useEffect } from 'react'
import { parentAPI } from '../api'
import { AlertTriangle, RefreshCw } from 'lucide-react'

const COLORS = {
    'Adult Content': 'bg-red-500/20 text-red-400 border-red-500/30',
    'Gambling': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    'Drug Related': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    'Cyberbullying': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    'Self Harm': 'bg-pink-500/20 text-pink-400 border-pink-500/30',
    'Violence': 'bg-red-700/20 text-red-400 border-red-700/30',
    'default': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
}

export default function AlertsPage({ selectedChild }) {
    const [threats, setThreats] = useState([])
    const [loading, setLoading] = useState(false)

    const load = async () => {
        if (!selectedChild) return
        setLoading(true)
        try {
            const r = await parentAPI.getThreats(selectedChild.id)
            setThreats(r.data)
        } catch (e) { }
        setLoading(false)
    }

    useEffect(() => { load() }, [selectedChild])

    if (!selectedChild) return <div className="flex justify-center items-center h-60"><p className="text-slate-500">Select a child to view alerts.</p></div>

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight">Threat Alerts</h1>
                    <p className="text-slate-500 text-sm mt-1">All detected threats for {selectedChild.name}</p>
                </div>
                <button onClick={load} className="flex items-center gap-2 px-4 py-2 bg-[#1e2d45] text-slate-300 rounded-xl text-sm hover:border-cyan-400 border border-[#1f3050] transition">
                    <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
                </button>
            </div>

            {loading && <div className="text-cyan-400 text-center py-8 animate-pulse">Loading…</div>}

            {!loading && threats.length === 0 && (
                <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-12 text-center">
                    <p className="text-6xl mb-3">✅</p>
                    <p className="text-white font-bold">No threats detected</p>
                    <p className="text-slate-500 text-sm mt-1">Great — the child's activity is clean.</p>
                </div>
            )}

            <div className="space-y-3">
                {threats.map(t => {
                    const cls = COLORS[t.type] || COLORS.default
                    return (
                        <div key={t.id} className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-5 hover:border-cyan-400/20 transition">
                            <div className="flex items-start gap-4">
                                <AlertTriangle size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 flex-wrap mb-2">
                                        <span className={`text-xs font-bold rounded-full px-2.5 py-1 border ${cls}`}>{t.type}</span>
                                        <span className="text-xs bg-[#1e2d45] text-slate-400 rounded-full px-2.5 py-1 border border-[#1f3050]">
                                            {t.confidence}% confidence
                                        </span>
                                        <span className="text-xs text-slate-500 uppercase tracking-wider">{t.source}</span>
                                        <span className="text-xs text-slate-600 ml-auto">{new Date(t.ts).toLocaleString()}</span>
                                    </div>
                                    {t.text && (
                                        <p className="text-slate-400 text-sm bg-[#0f1523] rounded-lg px-3 py-2 font-mono truncate">
                                            {t.text.slice(0, 150)}{t.text.length > 150 ? '…' : ''}
                                        </p>
                                    )}
                                    <p className="text-xs text-slate-600 mt-1.5">Action: {t.action}</p>
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
