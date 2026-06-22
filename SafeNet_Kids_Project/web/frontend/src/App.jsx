import { useState, useEffect } from 'react'
import { api } from './api'
import LoginPage from './pages/LoginPage'
import DashboardLayout from './pages/DashboardLayout'
import './index.css'

export default function App() {
  const [user, setUser] = useState(null)   // null = loading, false = not logged in
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.me().then(({ ok, data }) => {
      setUser(data.logged_in ? data : false)
      setLoading(false)
    }).catch(() => { setUser(false); setLoading(false) })
  }, [])

  if (loading) return (
    <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-root)' }}>
      <div style={{ color: 'var(--cyan)', fontSize: 24, fontWeight: 700 }}>🛡️ Loading…</div>
    </div>
  )

  if (!user) return <LoginPage onLogin={setUser} />

  return <DashboardLayout user={user} onLogout={() => setUser(false)} />
}
