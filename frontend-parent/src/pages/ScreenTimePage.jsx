import { useState, useEffect } from 'react'
import { parentAPI } from '../api'
import { BarChart2 } from 'lucide-react'
import { Bar } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

export default function ScreenTimePage({ selectedChild }) {
    const [chartData, setChartData] = useState(null)

    useEffect(() => {
        if (!selectedChild) return
        parentAPI.getScreentimeStats(selectedChild.id)
            .then(r => {
                const days = r.data.days || []
                setChartData({
                    labels: days.map(d => d.date),
                    datasets: [{
                        label: 'Activity Events',
                        data: days.map(d => d.count),
                        backgroundColor: 'rgba(0,212,255,0.25)',
                        borderColor: '#00d4ff',
                        borderWidth: 2,
                        borderRadius: 8,
                    }]
                })
            }).catch(() => { })
    }, [selectedChild])

    return (
        <div className="space-y-6 max-w-2xl">
            <div>
                <h1 className="text-3xl font-black text-white tracking-tight">Screen Time</h1>
                <p className="text-slate-500 text-sm mt-1">
                    Daily monitored activity for {selectedChild?.name || 'your child'} over the last 7 days
                </p>
            </div>

            {!selectedChild && (
                <div className="bg-slate-700/20 border border-slate-600/20 rounded-xl p-6 text-slate-500 text-sm">
                    Select a child from the top bar to view screen time data.
                </div>
            )}

            {selectedChild && !chartData && (
                <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-8 flex items-center justify-center">
                    <div className="text-cyan-400 animate-pulse text-sm font-semibold">Loading chart…</div>
                </div>
            )}

            {chartData && (
                <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-6">
                    <h2 className="text-white font-bold text-sm flex items-center gap-2 mb-4">
                        <BarChart2 size={15} className="text-cyan-400" /> 7-Day Activity Chart
                    </h2>
                    <Bar data={chartData} options={{
                        responsive: true,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { ticks: { color: '#475569' }, grid: { display: false } },
                            y: {
                                ticks: { color: '#475569' },
                                grid: { color: '#1f3050' },
                                beginAtZero: true
                            }
                        }
                    }} />
                    <p className="text-slate-600 text-xs mt-3 text-center">
                        Each bar = number of monitored events recorded that day
                    </p>
                </div>
            )}

            {chartData && (
                <div className="grid grid-cols-3 gap-4">
                    {[
                        { label: 'Total (7d)', value: chartData.datasets[0].data.reduce((a, b) => a + b, 0) },
                        { label: 'Peak Day', value: Math.max(...chartData.datasets[0].data) },
                        { label: 'Daily Avg', value: Math.round(chartData.datasets[0].data.reduce((a, b) => a + b, 0) / 7) },
                    ].map(s => (
                        <div key={s.label} className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-4 text-center">
                            <div className="text-3xl font-black text-cyan-400">{s.value}</div>
                            <div className="text-slate-500 text-xs mt-1">{s.label}</div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
