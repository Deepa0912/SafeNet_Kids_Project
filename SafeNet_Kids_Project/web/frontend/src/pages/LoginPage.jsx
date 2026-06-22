import { useState } from 'react'
import { api } from '../api'

export default function LoginPage({ onLogin }) {
    const [view, setView] = useState('login') // 'login' | 'register' | 'forgot'
    return (
        <div className="auth-overlay">
            <div className="auth-card">
                <div className="auth-logo">
                    <span className="shield-icon">🛡️</span>
                    <h1>SafeNet <span className="accent">Kids</span></h1>
                    <p className="subtitle">Intelligent Child Protection System</p>
                </div>
                {view === 'login' && <LoginForm onLogin={onLogin} onRegister={() => setView('register')} onForgot={() => setView('forgot')} />}
                {view === 'register' && <RegisterForm onLogin={onLogin} onBack={() => setView('login')} />}
                {view === 'forgot' && <ForgotForm onBack={() => setView('login')} />}
            </div>
        </div>
    )
}

function LoginForm({ onLogin, onRegister, onForgot }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const submit = async (e) => {
        e.preventDefault()
        if (!username || !password) { setError('Please enter your username and password.'); return }
        setError(''); setLoading(true)
        const { ok, data } = await api.login(username, password)
        setLoading(false)
        if (ok) { onLogin(data) }
        else { setError(data.error || 'Incorrect username or password.') }
    }

    return (
        <form onSubmit={submit}>
            <h2>Parent Sign In</h2>
            <div className="input-group">
                <label>Username</label>
                <input autoFocus value={username} onChange={e => setUsername(e.target.value)} placeholder="Enter username" />
            </div>
            <div className="input-group">
                <label>Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter password" />
            </div>
            {error && <div className="error-msg">{error}</div>}
            <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Signing in…' : 'Sign In →'}
            </button>
            <p className="auth-link">Forgot password? <a href="#" onClick={e => { e.preventDefault(); onForgot() }}>Reset it</a></p>
            <p className="auth-link">No account? <a href="#" onClick={e => { e.preventDefault(); onRegister() }}>Create one</a></p>
        </form>
    )
}

function RegisterForm({ onLogin, onBack }) {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [parentPw, setParentPw] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const submit = async (e) => {
        e.preventDefault()
        setError(''); setLoading(true)
        const { ok, data } = await api.register(username, password, parentPw)
        if (!ok) { setLoading(false); setError(data.error || 'Registration failed.'); return }
        // auto-login
        const login = await api.login(username, password)
        setLoading(false)
        if (login.ok) onLogin(login.data)
        else setError('Registered! Please sign in.')
    }

    return (
        <form onSubmit={submit}>
            <h2>Create Account</h2>
            <div className="input-group"><label>Username</label><input autoFocus value={username} onChange={e => setUsername(e.target.value)} placeholder="Choose a username" /></div>
            <div className="input-group"><label>Login Password</label><input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 4 characters" /></div>
            <div className="input-group"><label>Parent / Admin Password</label><input type="password" value={parentPw} onChange={e => setParentPw(e.target.value)} placeholder="Separate admin password" /></div>
            {error && <div className="error-msg">{error}</div>}
            <button type="submit" className="btn-primary" disabled={loading}>{loading ? 'Creating…' : 'Create Account →'}</button>
            <p className="auth-link"><a href="#" onClick={e => { e.preventDefault(); onBack() }}>← Back to Sign In</a></p>
        </form>
    )
}

function ForgotForm({ onBack }) {
    const [username, setUsername] = useState('')
    const [parentPw, setParentPw] = useState('')
    const [newPw, setNewPw] = useState('')
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [loading, setLoading] = useState(false)

    const submit = async (e) => {
        e.preventDefault()
        setError(''); setSuccess(''); setLoading(true)
        const { ok, data } = await api.resetPassword(username, parentPw, newPw)
        setLoading(false)
        if (ok) { setSuccess('Password reset! You can now sign in.'); setTimeout(onBack, 2000) }
        else { setError(data.error || 'Reset failed.') }
    }

    return (
        <form onSubmit={submit}>
            <h2>Reset Password</h2>
            <p className="form-hint">Use your <strong>Parent/Admin password</strong> to verify identity.</p>
            <div className="input-group"><label>Username</label><input autoFocus value={username} onChange={e => setUsername(e.target.value)} placeholder="Your username" /></div>
            <div className="input-group"><label>Parent / Admin Password</label><input type="password" value={parentPw} onChange={e => setParentPw(e.target.value)} placeholder="Your admin password" /></div>
            <div className="input-group"><label>New Login Password</label><input type="password" value={newPw} onChange={e => setNewPw(e.target.value)} placeholder="At least 4 characters" /></div>
            {error && <div className="error-msg">{error}</div>}
            {success && <div className="success-msg">{success}</div>}
            <button type="submit" className="btn-primary" disabled={loading}>{loading ? 'Resetting…' : 'Reset Password →'}</button>
            <p className="auth-link"><a href="#" onClick={e => { e.preventDefault(); onBack() }}>← Back to Sign In</a></p>
        </form>
    )
}
