import { useState, useRef, useEffect } from 'react'
import { api } from '../api'

/**
 * PasswordModal — pops up before any write action.
 * Props:
 *   isOpen:   boolean
 *   onClose:  () => void
 *   onVerified: () => void   (called only when password is correct)
 *   actionLabel: string     (e.g. "Add Site", "Stop Monitor")
 */
export default function PasswordModal({ isOpen, onClose, onVerified, actionLabel = 'this action' }) {
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const inputRef = useRef(null)

    // Auto-focus input when modal opens
    useEffect(() => {
        if (isOpen) {
            setPassword('')
            setError('')
            setTimeout(() => inputRef.current?.focus(), 50)
        }
    }, [isOpen])

    if (!isOpen) return null

    const submit = async (e) => {
        e.preventDefault()
        if (!password) { setError('Please enter the parent password.'); return }
        setError(''); setLoading(true)
        const { ok, data } = await api.verifyParent(password)
        setLoading(false)
        if (ok) {
            setPassword('')
            onVerified()
        } else {
            setError(data.error || 'Incorrect password.')
        }
    }

    const handleClose = () => {
        setPassword('')
        setError('')
        onClose()
    }

    return (
        <>
            {/* Backdrop */}
            <div onClick={handleClose} style={{
                position: 'fixed', inset: 0,
                background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
                zIndex: 9000,
            }} />

            {/* Dialog */}
            <div style={{
                position: 'fixed', top: '50%', left: '50%',
                transform: 'translate(-50%, -50%)',
                zIndex: 9001, width: '100%', maxWidth: 380,
                background: 'var(--bg-card)', border: '1px solid var(--border)',
                borderRadius: 'var(--radius-lg)',
                boxShadow: '0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,212,255,0.1)',
                padding: '32px 28px', animation: 'slideUp .25s ease',
            }}>
                <div style={{ textAlign: 'center', marginBottom: 24 }}>
                    <div style={{ fontSize: 36, marginBottom: 8 }}>🔒</div>
                    <h3 style={{ fontSize: 17, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                        Parent Verification
                    </h3>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6 }}>
                        Enter your parent/admin password to <strong style={{ color: 'var(--text-secondary)' }}>{actionLabel}</strong>.
                    </p>
                </div>

                <form onSubmit={submit}>
                    <div className="input-group">
                        <label>Parent / Admin Password</label>
                        <input
                            ref={inputRef}
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            placeholder="Enter parent password"
                        />
                    </div>
                    {error && <div className="error-msg">{error}</div>}
                    <div style={{ display: 'flex', gap: 10, marginTop: 4 }}>
                        <button type="button" className="btn-secondary" style={{ flex: 1 }} onClick={handleClose}>
                            Cancel
                        </button>
                        <button type="submit" className="btn-primary" style={{ flex: 2 }} disabled={loading}>
                            {loading ? 'Verifying…' : 'Confirm →'}
                        </button>
                    </div>
                </form>
            </div>
        </>
    )
}
