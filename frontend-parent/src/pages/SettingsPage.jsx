import { useState, useEffect } from 'react'
import { parentAPI } from '../api'
import { Plus, MonitorSmartphone, ChevronRight, Download, Key, CheckCircle2, Mail, Bell, Save } from 'lucide-react'

export default function SettingsPage({ children, selectedChild, onChildAdded, onNavigate }) {
    const [childName, setChildName] = useState('')
    const [msg, setMsg] = useState('')
    const [alertEmail, setAlertEmail] = useState('')
    const [emailEnabled, setEmailEnabled] = useState(false)
    const [emailMsg, setEmailMsg] = useState('')

    useEffect(() => {
        parentAPI.getEmailSettings().then(r => {
            setAlertEmail(r.data.alert_email || '')
            setEmailEnabled(r.data.email_alerts_enabled || false)
        }).catch(() => { })
    }, [])

    const addChild = async (e) => {
        e.preventDefault()
        if (!childName.trim()) return
        try {
            const r = await parentAPI.addChild(childName.trim())
            const { link_code } = r.data
            setMsg(`✅ Child added! Linking code: ${link_code} — Give this code to the monitoring agent.`)
            setChildName('')
            if (onChildAdded) onChildAdded()
        } catch { setMsg('❌ Failed to add child.') }
    }

    const saveEmail = async () => {
        try {
            await parentAPI.saveEmailSettings({ alert_email: alertEmail, email_alerts_enabled: emailEnabled })
            setEmailMsg('✅ Email settings saved!')
            setTimeout(() => setEmailMsg(''), 3000)
        } catch { setEmailMsg('❌ Failed to save.') }
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

            {/* Email Alerts */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="text-white font-bold text-sm flex items-center gap-2">
                        <Mail size={14} className="text-cyan-400" /> Email Alerts
                    </h3>
                    <button onClick={() => setEmailEnabled(e => !e)}
                        className={`relative w-12 h-6 rounded-full transition-colors ${emailEnabled ? 'bg-cyan-400' : 'bg-slate-700'}`}>
                        <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${emailEnabled ? 'translate-x-7' : 'translate-x-1'}`} />
                    </button>
                </div>
                <p className="text-slate-500 text-xs">Receive an email whenever a threat is detected on your child's device.</p>
                <div className="flex gap-2">
                    <input
                        value={alertEmail}
                        onChange={e => setAlertEmail(e.target.value)}
                        placeholder="parent@email.com"
                        type="email"
                        className="flex-1 bg-[#1e2d45] border border-[#1f3050] rounded-xl text-white placeholder-slate-600 px-4 py-2.5 text-sm outline-none focus:border-cyan-400 transition"
                    />
                    <button onClick={saveEmail}
                        className="flex items-center gap-2 px-4 py-2.5 bg-cyan-400 text-black font-bold rounded-xl text-sm hover:opacity-90 transition">
                        <Save size={14} /> Save
                    </button>
                </div>
                {emailMsg && <p className="text-sm text-cyan-300 bg-cyan-400/5 border border-cyan-400/20 rounded-lg px-3 py-2">{emailMsg}</p>}
                <p className="text-slate-600 text-xs">💡 Configure SMTP_HOST, SMTP_USER, SMTP_PASS in Railway environment variables to enable sending.</p>
            </div>

            {/* Connect Device CTA */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-6">
                <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-xl bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center flex-shrink-0">
                        <MonitorSmartphone size={18} className="text-cyan-400" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-white font-bold text-sm">Connect Child Device</h3>
                        <p className="text-slate-500 text-xs mt-1 mb-4">
                            Install the SafeNet monitoring agent on your child's computer using the step-by-step guide.
                            Includes download links for all required files.
                        </p>
                        <div className="flex flex-wrap gap-3 text-xs text-slate-400 mb-4">
                            <span className="flex items-center gap-1.5"><Download size={11} className="text-purple-400" /> Download agent files</span>
                            <span className="flex items-center gap-1.5"><Key size={11} className="text-yellow-400" /> Enter linking code</span>
                            <span className="flex items-center gap-1.5"><CheckCircle2 size={11} className="text-emerald-400" /> Start monitoring</span>
                        </div>
                        <button
                            onClick={() => onNavigate && onNavigate('setup')}
                            className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black font-bold rounded-xl text-sm hover:opacity-90 transition">
                            Open Setup Guide <ChevronRight size={14} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
