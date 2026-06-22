import { useEffect, useState } from 'react'
import axios from 'axios'
import { Shield, Wifi, Lock, WifiOff, LogOut } from 'lucide-react'

export default function ChildStatus({ childInfo, onUnlink }) {
    const [status, setStatus] = useState({ device_locked: false, internet_paused: false })

    useEffect(() => {
        const poll = async () => {
            try {
                const r = await axios.post('/api/child/heartbeat', {
                    child_id: childInfo.child_id, is_online: true
                })
                setStatus(r.data)
            } catch { }
        }
        poll()
        const iv = setInterval(poll, 30000)
        return () => clearInterval(iv)
    }, [childInfo.child_id])

    return (
        <div className="min-h-screen flex items-center justify-center p-4"
            style={{ background: 'radial-gradient(ellipse at 50% 25%, rgba(0,212,255,.04) 0%, transparent 55%), #0a0d14' }}>
            <div className="w-full max-w-sm">

                <div className="text-center mb-8">
                    <div className="text-6xl mb-3 drop-shadow-[0_0_16px_rgba(0,212,255,.4)]">🛡️</div>
                    <h1 className="text-3xl font-black text-white">SafeNet <span className="text-cyan-400">Kids</span></h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Hi, <strong className="text-white">{childInfo.child_name}</strong> — Device Protected
                    </p>
                </div>

                <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-6 shadow-[0_4px_40px_rgba(0,0,0,.5)] space-y-3">

                    {/* Protection Active */}
                    <div className="flex items-center gap-3 bg-green-500/10 border border-green-500/20 rounded-xl px-4 py-3.5">
                        <Shield size={18} className="text-green-400 flex-shrink-0" />
                        <div>
                            <p className="text-green-400 font-bold text-sm">Protection Active</p>
                            <p className="text-slate-500 text-xs">AI monitoring is running on this device</p>
                        </div>
                        <span className="ml-auto w-2.5 h-2.5 rounded-full bg-green-400 shadow-[0_0_8px_rgba(0,230,118,.6)] animate-pulse flex-shrink-0" />
                    </div>

                    {/* Parent Connected */}
                    <div className="flex items-center gap-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl px-4 py-3.5">
                        <Wifi size={18} className="text-cyan-400 flex-shrink-0" />
                        <div>
                            <p className="text-cyan-400 font-bold text-sm">Parent Connected</p>
                            <p className="text-slate-500 text-xs">Parent dashboard is monitoring this device</p>
                        </div>
                    </div>

                    {/* Device Locked */}
                    {status.device_locked && (
                        <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3.5">
                            <Lock size={18} className="text-red-400 flex-shrink-0" />
                            <div>
                                <p className="text-red-400 font-bold text-sm">Device Locked</p>
                                <p className="text-slate-500 text-xs">Your parent has locked this device</p>
                            </div>
                        </div>
                    )}

                    {/* Internet Paused */}
                    {status.internet_paused && (
                        <div className="flex items-center gap-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl px-4 py-3.5">
                            <WifiOff size={18} className="text-yellow-400 flex-shrink-0" />
                            <div>
                                <p className="text-yellow-400 font-bold text-sm">Internet Paused</p>
                                <p className="text-slate-500 text-xs">Your parent has paused internet access</p>
                            </div>
                        </div>
                    )}

                    <div className="border-t border-[#1f3050] pt-3 flex items-center justify-between">
                        <p className="text-xs text-slate-500">This device is safe &amp; monitored 🛡️</p>
                        <button onClick={onUnlink}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition border border-transparent hover:border-red-500/20">
                            <LogOut size={12} /> Unlink
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
