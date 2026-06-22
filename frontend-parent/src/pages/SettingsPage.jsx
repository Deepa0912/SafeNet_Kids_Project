import { useState } from 'react'
import { parentAPI } from '../api'
import { Plus } from 'lucide-react'

export default function SettingsPage({ children, selectedChild, onChildAdded }) {
    const [childName, setChildName] = useState('')
    const [msg, setMsg] = useState('')

    const addChild = async (e) => {
        e.preventDefault()
        if (!childName.trim()) return
        try {
            const r = await parentAPI.addChild(childName.trim())
            const { link_code } = r.data
            setMsg(`✅ Child added! Linking code: ${link_code} — Give this code to the monitoring agent.`)
            setChildName('')
            if (onChildAdded) onChildAdded()  // 🔄 Refresh children list
        } catch { setMsg('❌ Failed to add child.') }

    }

    return (
        <div className="space-y-6 max-w-xl">
            <div>
                <h1 className="text-3xl font-black text-white tracking-tight">Settings</h1>
                <p className="text-slate-500 text-sm mt-1">Manage child profiles and device linking</p>
            </div>

            {/* Add child */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-6">
                <h3 className="text-white font-bold text-sm mb-4">Add Child Profile</h3>
                <form onSubmit={addChild} className="flex gap-2">
                    <input value={childName} onChange={e => setChildName(e.target.value)} placeholder="Child's name"
                        className="flex-1 bg-[#1e2d45] border border-[#1f3050] rounded-xl text-white placeholder-slate-600 px-4 py-2.5 text-sm outline-none focus:border-cyan-400" />
                    <button type="submit"
                        className="flex items-center gap-2 px-4 py-2.5 bg-cyan-400 text-black font-bold rounded-xl text-sm hover:opacity-90 transition">
                        <Plus size={14} /> Add
                    </button>
                </form>
                {msg && <p className="mt-3 text-sm text-cyan-300 bg-cyan-400/5 border border-cyan-400/20 rounded-lg px-3 py-2">{msg}</p>}
            </div>

            {/* Children list */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-6">
                <h3 className="text-white font-bold text-sm mb-4">Registered Children</h3>
                {children.length === 0
                    ? <p className="text-slate-500 text-sm">No children added yet.</p>
                    : <div className="space-y-3">
                        {children.map(c => (
                            <div key={c.id} className="flex items-center gap-3 bg-[#0f1523] rounded-xl px-4 py-3 border border-[#1f3050]">
                                <span className="text-2xl">{c.is_online ? '🟢' : '⚫'}</span>
                                <div>
                                    <p className="text-white font-semibold text-sm">{c.name}</p>
                                    <p className="text-slate-500 text-xs">Link Code: <code className="text-cyan-400 font-mono">{c.link_code}</code></p>
                                </div>
                                <div className="ml-auto flex gap-2">
                                    {c.device_locked && <span className="text-xs bg-red-500/20 text-red-400 border border-red-500/30 rounded-full px-2 py-0.5">Locked</span>}
                                    {c.internet_paused && <span className="text-xs bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 rounded-full px-2 py-0.5">Internet Paused</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                }
            </div>

            {/* How to connect agent */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-6">
                <h3 className="text-white font-bold text-sm mb-3">How to Connect Child Device</h3>
                <ol className="text-slate-400 text-sm space-y-2 list-decimal list-inside">
                    <li>Add a child profile above to get a linking code.</li>
                    <li>Copy the linking code and go to the child's device.</li>
                    <li>Run: <code className="text-cyan-400 bg-[#0f1523] rounded px-2 py-0.5 font-mono text-xs">python agent/monitor.py</code></li>
                    <li>Enter the linking code when prompted.</li>
                    <li>Monitoring begins instantly. 🛡️</li>
                </ol>
            </div>
        </div>
    )
}
