import { useState } from 'react'
import { authAPI } from '../api'
import { Shield, Lock, Mail, User } from 'lucide-react'

export default function LoginPage({ onLogin }) {
    const [view, setView] = useState('login')
    return (
        <div className="min-h-screen bg-[#0a0d14] flex items-center justify-center p-4"
            style={{ background: 'radial-gradient(ellipse at 30% 40%, rgba(0,212,255,.06) 0%, transparent 60%), radial-gradient(ellipse at 80% 80%, rgba(124,77,255,.08) 0%, transparent 50%), #0a0d14' }}>
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="text-6xl mb-3 drop-shadow-[0_0_16px_rgba(0,212,255,.5)]">🛡️</div>
                    <h1 className="text-3xl font-black text-white">SafeNet <span className="text-cyan-400">Kids</span></h1>
                    <p className="text-slate-500 text-sm mt-1">AI-Powered Child Protection System</p>
                </div>
                <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-10 shadow-[0_4px_40px_rgba(0,0,0,.5),0_0_20px_rgba(0,212,255,.1)]">
                    {view === 'login' && <LoginForm onLogin={onLogin} onSwitch={setView} />}
                    {view === 'register' && <RegisterForm onLogin={onLogin} onSwitch={setView} />}
                    {view === 'forgot' && <ForgotForm onSwitch={setView} />}
                </div>
            </div>
        </div>
    )
}

function Field({ label, icon: Icon, ...props }) {
    return (
        <div className="mb-4">
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">{label}</label>
            <div className="relative">
                {Icon && <Icon size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />}
                <input {...props} className={`w-full bg-[#1e2d45] border border-[#1f3050] rounded-lg text-white placeholder-slate-600 py-2.5 pr-3 text-sm outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition ${Icon ? 'pl-9' : 'pl-3'}`} />
            </div>
        </div>
    )
}

function Btn({ loading, children, ...props }) {
    return (
        <button {...props} disabled={loading}
            className="w-full py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-cyan-400 text-black font-bold text-sm mt-2 hover:opacity-90 disabled:opacity-60 transition shadow-[0_4px_20px_rgba(0,212,255,.3)]">
            {loading ? 'Please wait…' : children}
        </button>
    )
}

function LoginForm({ onLogin, onSwitch }) {
    const [u, setU] = useState(''); const [p, setP] = useState('')
    const [err, setErr] = useState(''); const [loading, setLoading] = useState(false)
    const submit = async (e) => {
        e.preventDefault(); setErr(''); setLoading(true)
        try {
            const r = await authAPI.login(u, p)
            onLogin(r.data)
        } catch (ex) {
            setErr(ex.response?.data?.detail || 'Login failed.')
        } finally { setLoading(false) }
    }
    return (
        <form onSubmit={submit}>
            <h2 className="text-xl font-bold text-white mb-6">Parent Sign In</h2>
            <Field label="Username" icon={User} value={u} onChange={e => setU(e.target.value)} placeholder="Enter username" autoFocus />
            <Field label="Password" icon={Lock} type="password" value={p} onChange={e => setP(e.target.value)} placeholder="Enter password" />
            {err && <p className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 mb-3">{err}</p>}
            <Btn loading={loading}>Sign In →</Btn>
            <div className="text-center text-slate-500 text-xs mt-4 space-y-1">
                <p>Forgot password? <button type="button" onClick={() => onSwitch('forgot')} className="text-cyan-400 hover:underline">Reset it</button></p>
                <p>No account? <button type="button" onClick={() => onSwitch('register')} className="text-cyan-400 hover:underline">Register</button></p>
            </div>
        </form>
    )
}

function RegisterForm({ onLogin, onSwitch }) {
    const [u, setU] = useState(''); const [p, setP] = useState(''); const [em, setEm] = useState('')
    const [err, setErr] = useState(''); const [loading, setLoading] = useState(false)
    const submit = async (e) => {
        e.preventDefault(); setErr(''); setLoading(true)
        try { const r = await authAPI.register(u, p, em); onLogin(r.data) }
        catch (ex) { setErr(ex.response?.data?.detail || 'Registration failed.') }
        finally { setLoading(false) }
    }
    return (
        <form onSubmit={submit}>
            <h2 className="text-xl font-bold text-white mb-6">Create Parent Account</h2>
            <Field label="Username" icon={User} value={u} onChange={e => setU(e.target.value)} placeholder="Choose username" autoFocus />
            <Field label="Email (optional)" icon={Mail} type="email" value={em} onChange={e => setEm(e.target.value)} placeholder="your@email.com" />
            <Field label="Password" icon={Lock} type="password" value={p} onChange={e => setP(e.target.value)} placeholder="At least 8 characters" />
            {err && <p className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 mb-3">{err}</p>}
            <Btn loading={loading}>Create Account →</Btn>
            <p className="text-center text-slate-500 text-xs mt-4">
                Already have an account? <button type="button" onClick={() => onSwitch('login')} className="text-cyan-400 hover:underline">Sign in</button>
            </p>
        </form>
    )
}

function ForgotForm({ onSwitch }) {
    const [u, setU] = useState(''); const [p, setP] = useState('')
    const [msg, setMsg] = useState(''); const [err, setErr] = useState(''); const [loading, setLoading] = useState(false)
    const submit = async (e) => {
        e.preventDefault(); setMsg(''); setErr(''); setLoading(true)
        try { await authAPI.reset(u, p); setMsg('Password reset! You can now sign in.') }
        catch (ex) { setErr(ex.response?.data?.detail || 'Reset failed.') }
        finally { setLoading(false) }
    }
    return (
        <form onSubmit={submit}>
            <h2 className="text-xl font-bold text-white mb-6">Reset Password</h2>
            <Field label="Username" icon={User} value={u} onChange={e => setU(e.target.value)} placeholder="Your username" autoFocus />
            <Field label="New Password" icon={Lock} type="password" value={p} onChange={e => setP(e.target.value)} placeholder="New password" />
            {err && <p className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 mb-3">{err}</p>}
            {msg && <p className="text-green-400 text-xs bg-green-500/10 border border-green-500/20 rounded-lg px-3 py-2 mb-3">{msg}</p>}
            <Btn loading={loading}>Reset Password →</Btn>
            <p className="text-center text-slate-500 text-xs mt-4">
                <button type="button" onClick={() => onSwitch('login')} className="text-cyan-400 hover:underline">← Back to Sign In</button>
            </p>
        </form>
    )
}
