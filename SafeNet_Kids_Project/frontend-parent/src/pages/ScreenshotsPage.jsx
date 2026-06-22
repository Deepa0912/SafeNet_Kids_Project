import { useState, useEffect } from 'react'
import { parentAPI } from '../api'
import { Camera } from 'lucide-react'

export default function ScreenshotsPage({ selectedChild }) {
    const [screenshots, setScreenshots] = useState([])
    const [preview, setPreview] = useState(null)

    useEffect(() => {
        if (!selectedChild) return
        parentAPI.getScreenshots(selectedChild.id).then(r => setScreenshots(r.data)).catch(() => { })
    }, [selectedChild])

    if (!selectedChild) return <div className="flex justify-center items-center h-60"><p className="text-slate-500">Select a child to view screenshots.</p></div>

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-black text-white tracking-tight">Screenshot Evidence</h1>
                <p className="text-slate-500 text-sm mt-1">Captured during threat detection events</p>
            </div>

            {screenshots.length === 0
                ? <div className="bg-[#141d2e] border border-[#1f3050] rounded-xl p-12 text-center">
                    <Camera size={40} className="text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-500">No screenshots yet.</p>
                </div>
                : <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {screenshots.map(ss => (
                        <div key={ss.id} className="bg-[#141d2e] border border-[#1f3050] rounded-xl overflow-hidden cursor-pointer hover:border-cyan-400/40 transition"
                            onClick={() => setPreview(ss)}>
                            <img src={`/api/parent/screenshots/file/${ss.filename}`}
                                alt={ss.reason} className="w-full h-36 object-cover object-top bg-[#0f1523]"
                                onError={e => { e.target.style.display = 'none' }} />
                            <div className="p-3">
                                <p className="text-white text-xs font-semibold truncate">{ss.reason}</p>
                                <p className="text-slate-500 text-xs">{new Date(ss.ts).toLocaleString()}</p>
                            </div>
                        </div>
                    ))}
                </div>
            }

            {/* Lightbox */}
            {preview && (
                <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setPreview(null)}>
                    <div className="max-w-4xl w-full">
                        <img src={`/api/parent/screenshots/file/${preview.filename}`} alt={preview.reason}
                            className="w-full rounded-xl shadow-2xl" />
                        <p className="text-center text-white mt-3">{preview.reason} — {new Date(preview.ts).toLocaleString()}</p>
                    </div>
                </div>
            )}
        </div>
    )
}
