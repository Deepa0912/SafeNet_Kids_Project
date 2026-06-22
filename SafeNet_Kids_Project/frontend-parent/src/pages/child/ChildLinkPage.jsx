import { useState } from 'react'
import axios from 'axios'
import { Link, KeyRound } from 'lucide-react'

export default function ChildLinkPage({ onLinked }) {
    const [code, setCode] = useState('')
    const [err, setErr] = useState('')
    const [loading, setLoading] = useState(false)

    const deviceId = (() => {
        let id = localStorage.getItem('device_id')
        if (!id) { id = Math.random().toString(36).slice(2, 18); localStorage.setItem('device_id', id) }
        return id
    })()

    const submit = async (e) => {
        e.preventDefault(); setErr(''); setLoading(true)
        try {
            const r = await axios.post('/api/child/link', {
                link_code: code.trim().toUpperCase(), device_id: deviceId
            })
            onLinked(r.data)
        } catch (ex) {
            setErr(ex.response?.data?.detail || 'Invalid code. Please check and try again.')
        } finally { setLoading(false) }
    }

    return (
        <div className="min-h-screen flex items-center justify-center p-4"
            style={{ background: 'radial-gradient(ellipse at 50% 30%, rgba(0,230,118,.05) 0%, transparent 60%), #0a0d14' }}>
            <div className="w-full max-w-sm">

                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="text-6xl mb-3 drop-shadow-[0_0_16px_rgba(0,230,118,.4)]">🛡️</div>
                    <h1 className="text-3xl font-black text-white">SafeNet <span className="text-green-400">Kids</span></h1>
                    <p className="text-slate-500 text-sm mt-1">Child Device Setup</p>
                </div>

                <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-8 shadow-[0_4px_40px_rgba(0,0,0,.5),0_0_20px_rgba(0,230,118,.08)]">

                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-9 h-9 rounded-xl bg-green-500/20 border border-green-500/30 flex items-center justify-center">
                            <Link size={16} className="text-green-400" />
                        </div>
                        <div>
                            <h2 className="text-white font-bold text-base">Link to Parent</h2>
                            <p className="text-slate-500 text-xs">Enter the 6-character Linking Code from the parent's device</p>
                        </div>
                    </div>

                    <form onSubmit={submit}>
                        <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                            Linking Code
                        </label>
                        <div className="relative mb-4">
                            <KeyRound size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                            <input
                                value={code}
                                onChange={e => setCode(e.target.value.toUpperCase())}
                                placeholder="e.g. A1B2C3"
                                maxLength={12}
                                autoFocus
                                className="w-full bg-[#1e2d45] border border-[#1f3050] rounded-lg text-white placeholder-slate-600 py-3 pl-9 pr-3 text-sm font-mono tracking-widest outline-none focus:border-green-400 focus:ring-2 focus:ring-green-400/20 transition"
                            />
                        </div>
                        {err && (
                            <p className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 mb-3">
                                {err}
                            </p>
                        )}
                        <button type="submit" disabled={loading || !code.trim()}
                            className="w-full py-3 rounded-lg bg-gradient-to-r from-green-500 to-emerald-400 text-black font-bold text-sm hover:opacity-90 disabled:opacity-50 transition shadow-[0_4px_20px_rgba(0,230,118,.25)]">
                            {loading ? 'Connecting…' : 'Connect Device →'}
                        </button>
                    </form>

                    <p className="text-center text-slate-500 text-xs mt-5">
                        Get this code from the parent's dashboard under <strong className="text-slate-400">Settings → Children</strong>
                    </p>
                </div>

                {/* Back to parent link */}
                <p className="text-center text-slate-600 text-xs mt-4">
                    Are you a parent? <a href="/" className="text-cyan-400 hover:underline">Go to Parent Dashboard →</a>
                </p>
            </div>
        </div>
    )
}
