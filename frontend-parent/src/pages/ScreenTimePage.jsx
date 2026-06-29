import { useState, useEffect } from 'react'
import { parentAPI } from '../api'
import { Moon, Sun, Clock, Shield, Save, CheckCircle2, AlertCircle, BarChart2 } from 'lucide-react'
import { Bar } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

function HourSelect({ value, onChange, label }) {
    return (
        <div className="flex flex-col gap-1">
            <label className="text-slate-500 text-xs uppercase tracking-wider">{label}</label>
            <select value={value} onChange={e => onChange(parseInt(e.target.value))}
                className="bg-[#1e2d45] border border-[#1f3050] rounded-xl text-white px-3 py-2.5 text-sm outline-none focus:border-cyan-400 transition">
                {Array.from({ length: 24 }, (_, h) => (
                    <option key={h} value={h}>
                        {String(h).padStart(2, '0')}:00 — {h === 0 ? 'Midnight' : h < 12 ? `${h} AM` : h === 12 ? 'Noon' : `${h - 12} PM`}
                    </option>
                ))}
            </select>
        </div>
    )
}

function StatusBadge({ active }) {
    return active
        ? <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-2.5 py-1 rounded-full"><CheckCircle2 size={11} /> Active</span>
        : <span className="flex items-center gap-1.5 text-xs font-bold text-slate-400 bg-slate-700/40 border border-slate-600/30 px-2.5 py-1 rounded-full">Disabled</span>
}

export default function ScreenTimePage({ selectedChild }) {
    const [enabled, setEnabled] = useState(false)
    const [sleepHour, setSleepHour] = useState(22)
    const [wakeHour, setWakeHour] = useState(7)
    const [toast, setToast] = useState('')
    const [loading, setLoading] = useState(false)
    const [chartData, setChartData] = useState(null)

    const notify = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000) }

    useEffect(() => {
        if (!selectedChild) return
        parentAPI.getBedtime(selectedChild.id)
            .then(r => {
                setEnabled(r.data.enabled)
                setSleepHour(r.data.sleep_hour)
                setWakeHour(r.data.wake_hour)
            }).catch(() => { })
        parentAPI.getScreentimeStats(selectedChild.id)
            .then(r => {
                const days = r.data.days || []
                setChartData({
                    labels: days.map(d => d.date),
                    datasets: [{
                        label: 'Activity Events',
                        data: days.map(d => d.count),
                        backgroundColor: 'rgba(0,212,255,0.3)',
                        borderColor: '#00d4ff',
                        borderWidth: 2,
                        borderRadius: 6,
                    }]
                })
            }).catch(() => { })
    }, [selectedChild])

    const save = async () => {
        if (!selectedChild) { notify('⚠️ Select a child first.'); return }
        setLoading(true)
        try {
            await parentAPI.setBedtime(selectedChild.id, { enabled, sleep_hour: sleepHour, wake_hour: wakeHour })
            notify('✅ Bedtime schedule saved!')
        } catch { notify('❌ Failed to save.') }
        setLoading(false)
    }

    const fmt = h => `${String(h).padStart(2, '0')}:00`
    const now = new Date().getHours()
    // Is it currently bedtime?
    let isBedtime = false
    if (enabled) {
        if (sleepHour > wakeHour) isBedtime = now >= sleepHour || now < wakeHour
        else isBedtime = sleepHour <= now && now < wakeHour
    }

    return (
        <div className="space-y-6 max-w-2xl">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-black text-white tracking-tight">Screen Time & Bedtime</h1>
                <p className="text-slate-500 text-sm mt-1">
                    Schedule when {selectedChild?.name || 'your child'} can use their device
                </p>
            </div>

            {toast && (
                <div className="bg-green-500/10 border border-green-500/20 text-green-400 rounded-xl px-4 py-3 text-sm font-medium">
                    {toast}
                </div>
            )}

            {/* Current Status Card */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-white font-bold text-sm flex items-center gap-2">
                        <Clock size={15} className="text-cyan-400" /> Current Status
                    </h2>
                    <StatusBadge active={enabled} />
                </div>
                {enabled ? (
                    <div className={`rounded-xl p-4 flex items-center gap-4 ${isBedtime
                        ? 'bg-purple-500/10 border border-purple-500/20'
                        : 'bg-emerald-500/10 border border-emerald-500/20'}`}>
                        <span className="text-3xl">{isBedtime ? '🌙' : '☀️'}</span>
                        <div>
                            <p className={`font-bold text-sm ${isBedtime ? 'text-purple-300' : 'text-emerald-300'}`}>
                                {isBedtime ? 'Bedtime — Device locked' : 'Awake hours — Device allowed'}
                            </p>
                            <p className="text-slate-500 text-xs mt-0.5">
                                Sleep: {fmt(sleepHour)} → Wake: {fmt(wakeHour)} · Current: {fmt(now)}
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="bg-slate-700/20 border border-slate-600/20 rounded-xl p-4 flex items-center gap-3">
                        <AlertCircle size={16} className="text-slate-500" />
                        <p className="text-slate-500 text-sm">Bedtime mode is disabled. Enable it below to restrict device usage at night.</p>
                    </div>
                )}
            </div>

            {/* Schedule Config */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-6 space-y-5">
                <div className="flex items-center justify-between">
                    <h2 className="text-white font-bold text-sm flex items-center gap-2">
                        <Moon size={15} className="text-purple-400" /> Bedtime Schedule
                    </h2>
                    {/* Enable toggle */}
                    <button onClick={() => setEnabled(e => !e)}
                        className={`relative w-12 h-6 rounded-full transition-colors ${enabled ? 'bg-cyan-400' : 'bg-slate-700'}`}>
                        <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${enabled ? 'translate-x-7' : 'translate-x-1'}`} />
                    </button>
                </div>

                <p className="text-slate-500 text-xs">
                    Device will be locked between <strong className="text-white">{fmt(sleepHour)}</strong> and <strong className="text-white">{fmt(wakeHour)}</strong>.
                    The agent checks every 15 seconds.
                </p>

                <div className="grid grid-cols-2 gap-4">
                    <HourSelect value={sleepHour} onChange={setSleepHour} label="🌙 Sleep Time (lock)" />
                    <HourSelect value={wakeHour} onChange={setWakeHour} label="☀️ Wake Time (unlock)" />
                </div>

                {/* Visual timeline */}
                <div>
                    <p className="text-slate-500 text-xs uppercase tracking-wider mb-2">24-hour Timeline</p>
                    <div className="relative h-8 bg-emerald-500/20 rounded-full overflow-hidden border border-emerald-500/20">
                        {/* Locked region */}
                        {(() => {
                            const lockPct = (sleepHour / 24) * 100
                            const wakePct = (wakeHour / 24) * 100
                            const isWrapped = sleepHour > wakeHour
                            return isWrapped ? (
                                <>
                                    <div className="absolute top-0 left-0 h-full bg-purple-500/50" style={{ width: `${wakePct}%` }} />
                                    <div className="absolute top-0 h-full bg-purple-500/50" style={{ left: `${lockPct}%`, right: 0 }} />
                                </>
                            ) : (
                                <div className="absolute top-0 h-full bg-purple-500/50" style={{ left: `${lockPct}%`, width: `${wakePct - lockPct}%` }} />
                            )
                        })()}
                        {/* Now marker */}
                        <div className="absolute top-0 h-full w-0.5 bg-white/80" style={{ left: `${(now / 24) * 100}%` }} />
                        <div className="absolute top-0 bottom-0 flex items-center justify-between px-3 w-full pointer-events-none">
                            <span className="text-white/50 text-[10px]">12 AM</span>
                            <span className="text-white/50 text-[10px]">6 AM</span>
                            <span className="text-white/50 text-[10px]">12 PM</span>
                            <span className="text-white/50 text-[10px]">6 PM</span>
                            <span className="text-white/50 text-[10px]">12 AM</span>
                        </div>
                    </div>
                    <div className="flex gap-4 mt-2 text-xs text-slate-500">
                        <span className="flex items-center gap-1.5"><span className="w-3 h-3 bg-emerald-500/50 rounded-sm inline-block" /> Allowed hours</span>
                        <span className="flex items-center gap-1.5"><span className="w-3 h-3 bg-purple-500/50 rounded-sm inline-block" /> Locked hours</span>
                        <span className="flex items-center gap-1.5"><span className="w-0.5 h-3 bg-white/80 inline-block" /> Now</span>
                    </div>
                </div>

                <button onClick={save} disabled={loading}
                    className="flex items-center gap-2 px-5 py-2.5 bg-cyan-400 text-black font-bold rounded-xl text-sm hover:opacity-90 transition disabled:opacity-60">
                    {loading
                        ? <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin" />
                        : <Save size={14} />}
                    Save Schedule
                </button>
            </div>

            {/* 7-Day Activity Chart */}
            {chartData && (
                <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-6">
                    <h2 className="text-white font-bold text-sm flex items-center gap-2 mb-4">
                        <BarChart2 size={15} className="text-cyan-400" /> 7-Day Activity
                    </h2>
                    <Bar data={chartData} options={{
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { ticks: { color: '#475569' }, grid: { display: false } },
                            y: { ticks: { color: '#475569' }, grid: { color: '#1f3050' }, beginAtZero: true }
                        }
                    }} />
                    <p className="text-slate-600 text-xs mt-2 text-center">Daily monitored activity events</p>
                </div>
            )}
        </div>
    )
}
