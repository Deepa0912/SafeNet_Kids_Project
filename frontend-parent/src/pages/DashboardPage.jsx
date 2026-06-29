import { useState, useEffect } from 'react'
import { parentAPI } from '../api'
import { Bar, Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from 'chart.js'
import { Activity, AlertTriangle, Shield, Globe, FileText, Sparkles } from 'lucide-react'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const chartOpts = { responsive: true, plugins: { legend: { labels: { color: '#8ba7c7' } } }, scales: { x: { ticks: { color: '#8ba7c7' } }, y: { ticks: { color: '#8ba7c7' }, grid: { color: '#1f3050' } } } }

const COLORS = { 'Adult Content': '#ff5252', 'Gambling': '#ffca28', 'Drug Related': '#ff9800', 'Cyberbullying': '#7c4dff', 'Self Harm': '#e91e63', 'Violence': '#f44336', Safe: '#00e676' }

export default function DashboardPage({ selectedChild }) {
    const [stats, setStats] = useState(null)
    const [activity, setActivity] = useState([])
    const [aiSummary, setAiSummary] = useState(null)
    const [aiLoading, setAiLoading] = useState(false)

    const generateSummary = async () => {
        if (!selectedChild) return
        setAiLoading(true)
        try {
            const r = await parentAPI.getAISummary(selectedChild.id)
            setAiSummary(r.data)
        } catch { setAiSummary({ summary: 'Could not generate summary. Check your connection.' }) }
        setAiLoading(false)
    }

    useEffect(() => {
        if (!selectedChild) return
        parentAPI.getDashboard(selectedChild.id).then(r => { setStats(r.data); setActivity(r.data.latest_activity || []) }).catch(() => { })
    }, [selectedChild])

    if (!selectedChild) return <Empty msg="No child device registered yet. Add a child profile in Settings." />
    if (!stats) return <Loading />

    const cats = stats.category_counts || {}
    const score = stats.risk_score || 0
    const riskColor = score < 30 ? '#00e676' : score < 70 ? '#ffca28' : '#ff5252'

    const doughnutData = {
        labels: Object.keys(cats).length ? Object.keys(cats) : ['Safe'],
        datasets: [{
            data: Object.keys(cats).length ? Object.values(cats) : [1],
            backgroundColor: Object.keys(cats).length ? Object.keys(cats).map(k => COLORS[k] || '#00d4ff') : ['#00e676'],
            borderWidth: 0
        }]
    }

    return (
        <div className="space-y-6">
            <PageHeader title={`${selectedChild.name}'s Dashboard`} subtitle="Real-time protection overview" />

            {/* Stat cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard label="Risk Score" value={score} badge={score < 30 ? 'Low' : score < 70 ? 'Medium' : 'High'} color={riskColor} />
                <StatCard label="Threats (7d)" value={stats.total_threats} badge="Last week" color="#00d4ff" />
                <StatCard label="Status" value={stats.child?.is_online ? '🟢' : '⚫'} badge={stats.child?.is_online ? 'Online' : 'Offline'} color="#00e676" />
                <StatCard label="Blocked Sites" value={stats.blocked_sites_count || 0} badge="Configured" color="#7c4dff" />
            </div>

            {/* Download Report row */}
            <div className="flex items-center justify-between bg-[#141d2e] border border-[#1f3050] rounded-xl px-5 py-3">
                <div className="flex items-center gap-3">
                    <FileText size={16} className="text-purple-400" />
                    <div>
                        <p className="text-white font-semibold text-sm">Safety Report</p>
                        <p className="text-slate-500 text-xs">Download a PDF summary of activity and threats</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    {['weekly', 'monthly'].map(period => (
                        <button key={period} onClick={() => parentAPI.downloadReport(selectedChild.id, period)}
                            className="px-3 py-1.5 bg-[#1e2d45] border border-[#1f3050] text-slate-300 text-xs font-semibold rounded-lg hover:border-purple-400/40 hover:text-purple-300 transition capitalize">
                            {period}
                        </button>
                    ))}
                </div>
            </div>

            {/* Charts row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card title="Threat Categories">
                    <div className="flex justify-center py-2">
                        <div style={{ width: 220, height: 220 }}>
                            <Doughnut data={doughnutData} options={{ responsive: true, plugins: { legend: { labels: { color: '#8ba7c7', boxWidth: 14, font: { size: 12 } } } } }} />
                        </div>
                    </div>
                </Card>

                <Card title="Live Activity Feed">
                    {activity.length === 0
                        ? <p className="text-slate-500 text-sm text-center py-6">No recent activity.</p>
                        : <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                            {activity.map((a, i) => (
                                <div key={i} className="flex items-start gap-3 bg-[#0f1523] rounded-lg px-3 py-2">
                                    <span className="text-xs bg-[#1e2d45] text-cyan-400 rounded px-1.5 py-0.5 uppercase font-mono flex-shrink-0">{a.type}</span>
                                    <span className="text-slate-300 text-xs truncate">{a.value}</span>
                                    <span className="text-slate-600 text-xs ml-auto flex-shrink-0">{new Date(a.ts).toLocaleTimeString()}</span>
                                </div>
                            ))}
                        </div>
                    }
                </Card>
            </div>

            {/* AI Summary */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-5">
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <Sparkles size={15} className="text-yellow-400" />
                        <h3 className="text-white font-bold text-sm">Weekly AI Safety Summary</h3>
                    </div>
                    <button onClick={generateSummary} disabled={aiLoading}
                        className="flex items-center gap-2 px-3 py-1.5 bg-yellow-400/10 border border-yellow-400/20 text-yellow-400 text-xs font-semibold rounded-lg hover:bg-yellow-400/20 transition disabled:opacity-50">
                        {aiLoading
                            ? <div className="w-3 h-3 border-2 border-yellow-400 border-t-transparent rounded-full animate-spin" />
                            : <Sparkles size={11} />}
                        {aiLoading ? 'Generating…' : 'Generate'}
                    </button>
                </div>
                {aiSummary
                    ? <div className="space-y-3">
                        <p className="text-slate-300 text-sm leading-relaxed italic">"{aiSummary.summary}"</p>
                        {aiSummary.threat_count !== undefined && (
                            <div className="flex gap-4 text-xs text-slate-500">
                                <span>🛡️ {aiSummary.threat_count} threats</span>
                                <span>📊 {aiSummary.activity_count} events</span>
                                {Object.entries(aiSummary.categories || {}).map(([k, v]) => (
                                    <span key={k}>⚠️ {k}: {v}</span>
                                ))}
                            </div>
                        )}
                    </div>
                    : <p className="text-slate-600 text-sm">Click Generate to get a Gemini AI summary of this week's safety report.</p>
                }
            </div>
        </div>
    )
}

function StatCard({ label, value, badge, color }) {
    return (
        <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-5 hover:border-cyan-400/30 transition">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</div>
            <div className="text-4xl font-black" style={{ color }}>{value}</div>
            <div className="mt-2 text-xs text-slate-500 bg-[#0f1523] rounded-full px-2 py-0.5 inline-block border border-[#1f3050]">{badge}</div>
        </div>
    )
}

function Card({ title, children }) {
    return (
        <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-5">
            <h3 className="text-white font-bold text-sm mb-4">{title}</h3>
            {children}
        </div>
    )
}

function PageHeader({ title, subtitle }) {
    return <div><h1 className="text-3xl font-black text-white tracking-tight">{title}</h1><p className="text-slate-500 text-sm mt-1">{subtitle}</p></div>
}

function Empty({ msg }) {
    return <div className="flex items-center justify-center h-60"><p className="text-slate-500 text-sm text-center max-w-xs">{msg}</p></div>
}

function Loading() {
    return <div className="flex items-center justify-center h-60"><div className="text-cyan-400 text-lg font-bold animate-pulse">Loading…</div></div>
}
