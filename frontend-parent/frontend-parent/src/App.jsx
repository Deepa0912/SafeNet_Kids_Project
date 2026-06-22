import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import ChildLinkPage from './pages/child/ChildLinkPage'
import ChildStatus from './pages/child/ChildStatus'
import './index.css'

// ── Parent App ────────────────────────────────────────────────────────────────
function ParentApp() {
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem('token')
    const username = localStorage.getItem('username')
    return token ? { token, username } : null
  })

  const handleLogin = (data) => {
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('parent_id', data.id ?? '')
    setUser({ token: data.access_token, username: data.username })
  }

  const handleLogout = () => {
    localStorage.clear()
    setUser(null)
  }

  return user
    ? <Dashboard user={user} onLogout={handleLogout} />
    : <LoginPage onLogin={handleLogin} />
}

// ── Child App ─────────────────────────────────────────────────────────────────
function ChildApp() {
  const [childInfo, setChildInfo] = useState(() => {
    const s = localStorage.getItem('child_info')
    return s ? JSON.parse(s) : null
  })

  const handleLinked = (info) => {
    localStorage.setItem('child_info', JSON.stringify(info))
    setChildInfo(info)
  }

  const handleUnlink = () => {
    localStorage.removeItem('child_info')
    setChildInfo(null)
  }

  return childInfo
    ? <ChildStatus childInfo={childInfo} onUnlink={handleUnlink} />
    : <ChildLinkPage onLinked={handleLinked} />
}

// ── Router Root ───────────────────────────────────────────────────────────────
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Parent routes */}
        <Route path="/*" element={<ParentApp />} />
        {/* Child device route */}
        <Route path="/child" element={<ChildApp />} />
        <Route path="/child/*" element={<ChildApp />} />
      </Routes>
    </BrowserRouter>
  )
}
