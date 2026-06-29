import { useState, useEffect } from 'react'
import { parentAPI } from '../api'
import { Lock, Plus, Trash2, Shield } from 'lucide-react'

function ControlBtn({ icon: Icon, label, onClick, color = 'bg-[#1e2d45]', textColor = 'text-white' }) {
    const [loading, setLoading] = useState(false)
    const handle = async () => { setLoading(true); await onClick(); setLoading(false) }
    return (
        <button onClick={handle} disabled={loading}
            className={`flex items-center gap-3 px-5 py-3 rounded-xl ${color} ${textColor} border border-[#1f3050] hover:border-cyan-400/40 font-semibold text-sm transition disabled:opacity-60`}>
            {loading ? <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" /> : <Icon size={16} />}
            {label}
        </button>
    )
}

export default function ControlPage({ selectedChild, children }) {
    const [sites, setSites] = useState([])
    const [apps, setApps] = useState([])
    const [newSite, setNewSite] = useState('')
    const [newApp, setNewApp] = useState('')
    const [toast, setToast] = useState('')

    const notify = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000) }

    useEffect(() => {
        parentAPI.getBlockedSites().then(r => setSites(r.data)).catch(() => { })
        parentAPI.getBlockedApps().then(r => setApps(r.data)).catch(() => { })
    }, [])

    const control = async (action) => {
        if (!selectedChild) { notify('⚠️ No child selected — choose a child from the sidebar first.'); return }
        await parentAPI.controlDevice(selectedChild.id, action)
        notify(`✅ Applied: ${action}`)
    }

    const addSite = async (e) => {
        e.preventDefault()
        if (!newSite.trim()) return
        await parentAPI.addBlockedSite(newSite.trim(), selectedChild?.id)
        parentAPI.getBlockedSites().then(r => setSites(r.data))
        setNewSite('')
        notify('Site blocked!')
    }

    const removeSite = async (id) => {
        await parentAPI.removeBlockedSite(id)
        setSites(s => s.filter(x => x.id !== id))
        notify('Site unblocked.')
    }

    const addApp = async (e) => {
        e.preventDefault()
        if (!newApp.trim()) return
        await parentAPI.addBlockedApp(newApp.trim(), selectedChild?.id)
        parentAPI.getBlockedApps().then(r => setApps(r.data))
        setNewApp('')
        notify('App blocked!')
    }

    const removeApp = async (id) => {
        await parentAPI.removeBlockedApp(id)
        setApps(a => a.filter(x => x.id !== id))
        notify('App unblocked.')
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-black text-white tracking-tight">Control Center</h1>
                <p className="text-slate-500 text-sm mt-1">Remotely manage {selectedChild?.name || 'child'}'s device</p>
            </div>

            {toast && (
                <div className="bg-green-500/10 border border-green-500/20 text-green-400 rounded-xl px-4 py-3 text-sm font-medium">
                    ✓ {toast}
                </div>
            )}

            {/* Device Controls */}
            <Section title="Device Controls" icon={Shield}>
                <div className="flex flex-wrap gap-3">
                    <ControlBtn icon={Lock} label="🔒 Lock Device" onClick={() => control('lock')} color="bg-red-500/10" textColor="text-red-400" />
                </div>
            </Section>

            {/* Blocked Sites */}
            <Section title="Blocked Websites" icon={Shield}>
                <form onSubmit={addSite} className="flex gap-2 mb-4">
                    <input value={newSite} onChange={e => setNewSite(e.target.value)} placeholder="e.g. example.com"
                        className="flex-1 bg-[#1e2d45] border border-[#1f3050] rounded-xl text-white placeholder-slate-600 px-4 py-2.5 text-sm outline-none focus:border-cyan-400 transition" />
                    <button type="submit" className="flex items-center gap-2 px-4 py-2.5 bg-cyan-400 text-black font-bold rounded-xl text-sm hover:opacity-90 transition">
                        <Plus size={14} /> Block
                    </button>
                </form>
                <div className="flex flex-wrap gap-2">
                    {sites.length === 0 && <p className="text-slate-500 text-sm">No sites blocked.</p>}
                    {sites.map(s => (
                        <div key={s.id} className="flex items-center gap-2 bg-[#1e2d45] border border-[#1f3050] rounded-full px-3 py-1.5 text-sm text-slate-300">
                            {s.url}
                            <button onClick={() => removeSite(s.id)} className="text-slate-500 hover:text-red-400 transition"><Trash2 size={12} /></button>
                        </div>
                    ))}
                </div>
            </Section>

            {/* Blocked Apps */}
            <Section title="Blocked Applications" icon={Lock}>
                <form onSubmit={addApp} className="flex gap-2 mb-4">
                    <input value={newApp} onChange={e => setNewApp(e.target.value)} placeholder="e.g. chrome.exe"
                        className="flex-1 bg-[#1e2d45] border border-[#1f3050] rounded-xl text-white placeholder-slate-600 px-4 py-2.5 text-sm outline-none focus:border-cyan-400 transition" />
                    <button type="submit" className="flex items-center gap-2 px-4 py-2.5 bg-purple-500 text-white font-bold rounded-xl text-sm hover:opacity-90 transition">
                        <Plus size={14} /> Block App
                    </button>
                </form>
                <div className="flex flex-wrap gap-2">
                    {apps.length === 0 && <p className="text-slate-500 text-sm">No apps blocked.</p>}
                    {apps.map(a => (
                        <div key={a.id} className="flex items-center gap-2 bg-[#1e2d45] border border-[#1f3050] rounded-full px-3 py-1.5 text-sm text-slate-300">
                            {a.app_name}
                            <button onClick={() => removeApp(a.id)} className="text-slate-500 hover:text-red-400 transition"><Trash2 size={12} /></button>
                        </div>
                    ))}
                </div>
            </Section>
        </div>
    )
}

function Section({ title, icon: Icon, children }) {
    return (
        <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-6">
            <h3 className="text-white font-bold text-sm mb-4 flex items-center gap-2">
                <Icon size={15} className="text-cyan-400" /> {title}
            </h3>
            {children}
        </div>
    )
}
