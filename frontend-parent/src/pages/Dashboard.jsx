import { useState, useEffect, useCallback } from 'react'
import { io } from 'socket.io-client'
import { parentAPI } from '../api'
import {
    LayoutDashboard, Bell, Camera, Shield,
    Settings, LogOut, MonitorSmartphone, Sun, Moon
} from 'lucide-react'
import DashboardPage from './DashboardPage'
import AlertsPage from './AlertsPage'
import ScreenshotsPage from './ScreenshotsPage'
import ControlPage from './ControlPage'
import SettingsPage from './SettingsPage'
import SetupGuidePage from './SetupGuidePage'

const NAV = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'alerts', icon: Bell, label: 'Alerts' },
    { id: 'screenshots', icon: Camera, label: 'Screenshots' },
    { id: 'control', icon: Shield, label: 'Control Center' },
    { id: 'setup', icon: MonitorSmartphone, label: 'Connect Device' },
    { id: 'settings', icon: Settings, label: 'Settings' },
]

const THREAT_COLORS = {
    'Adult Content': 'bg-red-500',
    'Gambling': 'bg-yellow-500',
    'Drug Related': 'bg-orange-500',
    'Cyberbullying': 'bg-purple-500',
    'Self Harm': 'bg-pink-500',
    'Violence': 'bg-red-700',
}

export default function Dashboard({ user, onLogout }) {
    const [page, setPage] = useState('dashboard')
    const [theme, setTheme] = useState(() => localStorage.getItem('sn_theme') || 'dark')

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme)
        localStorage.setItem('sn_theme', theme)
    }, [theme])

    const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark')
    const [children, setChildren] = useState([])
    const [selectedChild, setSelectedChild] = useState(null)
    const [toasts, setToasts] = useState([])
    const [unreadCount, setUnreadCount] = useState(0)

    // Load children
    const refreshChildren = useCallback(() => {
        parentAPI.getChildren().then(r => {
            setChildren(r.data)
            if (r.data.length > 0 && !selectedChild) setSelectedChild(r.data[0])
        }).catch(() => { })
    }, [selectedChild])

    useEffect(() => {
        refreshChildren()
        parentAPI.getNotifications().then(r => {
            setUnreadCount(r.data.filter(n => !n.is_read).length)
        }).catch(() => { })
    }, [])


    // Socket.IO real-time alerts
    useEffect(() => {
        const parentId = localStorage.getItem('parent_id')
        if (!parentId) return
        const socket = io({ path: '/socket.io', transports: ['websocket', 'polling'] })
        socket.on('connect', () => {
            socket.emit('join_parent_room', { parent_id: parseInt(parentId) })
        })
        socket.on('threat_alert', (data) => {
            addToast({
                id: Date.now(),
                type: data.threat_type,
                message: `⚠️ ${data.threat_type} detected on ${data.child_name}'s device`,
                detail: data.text?.slice(0, 80),
                color: THREAT_COLORS[data.threat_type] || 'bg-red-500',
            })
            setUnreadCount(n => n + 1)
        })
        socket.on('new_screenshot', (data) => {
            addToast({ id: Date.now(), type: 'screenshot', message: `📷 New screenshot from ${data.child_name}`, color: 'bg-blue-500' })
        })
        return () => socket.disconnect()
    }, [])

    const addToast = (toast) => {
        setToasts(prev => [toast, ...prev].slice(0, 5))
        setTimeout(() => setToasts(prev => prev.filter(t => t.id !== toast.id)), 6000)
    }

    const renderPage = () => {
        const props = { selectedChild, children }
        switch (page) {
            case 'dashboard': return <DashboardPage  {...props} />
            case 'alerts': return <AlertsPage     {...props} />
            case 'screenshots': return <ScreenshotsPage {...props} />
            case 'control': return <ControlPage    {...props} />
            case 'setup': return <SetupGuidePage />
            case 'settings': return <SettingsPage   {...props} onChildAdded={refreshChildren} />
            default: return <DashboardPage  {...props} />
        }
    }

    return (
        <div className="flex h-screen bg-[#0a0d14] overflow-hidden">

            {/* Sidebar */}
            <aside className="w-60 flex-shrink-0 bg-[#0d1117] border-r border-[#1f3050] flex flex-col">
                <div className="px-5 py-7 border-b border-[#1f3050]">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl drop-shadow-[0_0_8px_rgba(0,212,255,.5)]">🛡️</span>
                        <div>
                            <div className="text-white font-black text-lg leading-tight">SafeNet</div>
                            <div className="text-cyan-400 font-bold text-sm leading-tight">Kids</div>
                        </div>
                    </div>
                </div>

                {/* Child selector */}
                {children.length > 0 && (
                    <div className="px-3 py-3 border-b border-[#1f3050]">
                        <label className="text-xs text-slate-500 uppercase tracking-wider px-2 mb-1 block">Monitoring</label>
                        <select
                            value={selectedChild?.id || ''}
                            onChange={e => setSelectedChild(children.find(c => c.id === parseInt(e.target.value)))}
                            className="w-full bg-[#1e2d45] border border-[#1f3050] rounded-lg text-white text-sm px-3 py-2 outline-none focus:border-cyan-400">
                            {children.map(c => (
                                <option key={c.id} value={c.id}>{c.name} {c.is_online ? '🟢' : '⚫'}</option>
                            ))}
                        </select>
                    </div>
                )}

                {/* Nav */}
                <nav className="flex-1 px-3 py-4 space-y-1">
                    {NAV.map(({ id, icon: Icon, label }) => (
                        <button key={id} onClick={() => setPage(id)}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition ${page === id
                                ? 'bg-cyan-400/10 text-cyan-400'
                                : 'text-slate-400 hover:bg-white/5 hover:text-white'
                                }`}>
                            <Icon size={17} />
                            <span>{label}</span>
                            {id === 'alerts' && unreadCount > 0 && (
                                <span className="ml-auto bg-red-500 text-white text-xs font-bold rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
                                    {unreadCount > 99 ? '99+' : unreadCount}
                                </span>
                            )}
                        </button>
                    ))}
                </nav>

                {/* Footer */}
                <div className="px-3 py-3 border-t border-[#1f3050] flex items-center gap-2">
                    <div className="flex-1 min-w-0">
                        <div className="text-white text-sm font-semibold truncate">{user.username}</div>
                        <div className="text-slate-500 text-xs">Parent Admin</div>
                    </div>
                    <button onClick={toggleTheme} title={theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}
                        className="p-2 rounded-lg bg-yellow-400/10 text-yellow-400 hover:bg-yellow-400/20 transition">
                        {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                    </button>
                    <button onClick={onLogout} title="Sign out"
                        className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition">
                        <LogOut size={16} />
                    </button>
                </div>
            </aside>

            {/* Main */}
            <main className="flex-1 overflow-y-auto"
                style={{ background: 'radial-gradient(ellipse at 70% 10%, rgba(0,212,255,.03) 0%, transparent 50%), #0f1523' }}>
                <div className="p-8">{renderPage()}</div>
            </main>

            {/* Real-time Toast Notifications */}
            <div className="fixed top-4 right-4 space-y-3 z-50">
                {toasts.map(toast => (
                    <div key={toast.id}
                        className="toast-enter bg-[#141d2e] border border-[#1f3050] rounded-xl p-4 w-80 shadow-2xl">
                        <div className="flex items-start gap-3">
                            <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${toast.color}`} />
                            <div>
                                <p className="text-white text-sm font-semibold">{toast.message}</p>
                                {toast.detail && <p className="text-slate-400 text-xs mt-0.5 truncate">{toast.detail}</p>}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
