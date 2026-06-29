import { useState } from 'react'
import {
    Monitor, Download, Terminal, Key, CheckCircle2,
    Copy, ChevronRight, AlertCircle, BookOpen, Wifi,
    Shield, Cpu, PlayCircle
} from 'lucide-react'

const steps = [
    {
        id: 1,
        icon: Monitor,
        color: 'text-cyan-400',
        bg: 'bg-cyan-400/10',
        border: 'border-cyan-400/20',
        title: 'Prerequisites',
        subtitle: 'What the child\'s PC needs',
        content: <StepPrerequisites />,
    },
    {
        id: 2,
        icon: Download,
        color: 'text-purple-400',
        bg: 'bg-purple-400/10',
        border: 'border-purple-400/20',
        title: 'Download Agent',
        subtitle: 'Get the monitoring files',
        content: <StepDownload />,
    },
    {
        id: 3,
        icon: Terminal,
        color: 'text-green-400',
        bg: 'bg-green-400/10',
        border: 'border-green-400/20',
        title: 'Install & Run',
        subtitle: 'Set up on child\'s device',
        content: <StepInstall />,
    },
    {
        id: 4,
        icon: Key,
        color: 'text-yellow-400',
        bg: 'bg-yellow-400/10',
        border: 'border-yellow-400/20',
        title: 'Link Device',
        subtitle: 'Enter the linking code',
        content: <StepLink />,
    },
    {
        id: 5,
        icon: CheckCircle2,
        color: 'text-emerald-400',
        bg: 'bg-emerald-400/10',
        border: 'border-emerald-400/20',
        title: 'Verify',
        subtitle: 'Confirm it\'s working',
        content: <StepVerify />,
    },
]

function CodeBlock({ code }) {
    const [copied, setCopied] = useState(false)
    const copy = () => {
        navigator.clipboard.writeText(code)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }
    return (
        <div className="relative group mt-2">
            <pre className="bg-[#0a0d14] border border-[#1f3050] rounded-xl px-4 py-3 text-cyan-300 text-sm font-mono overflow-x-auto whitespace-pre-wrap">
                {code}
            </pre>
            <button onClick={copy}
                className="absolute top-2 right-2 flex items-center gap-1.5 px-2.5 py-1 bg-[#1e2d45] border border-[#1f3050] rounded-lg text-xs text-slate-400 hover:text-white hover:border-cyan-400/40 transition opacity-0 group-hover:opacity-100">
                <Copy size={11} />
                {copied ? 'Copied!' : 'Copy'}
            </button>
        </div>
    )
}

function Pill({ color, text }) {
    return (
        <span className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${color}`}>
            {text}
        </span>
    )
}

/* ── Step Content Components ─────────────────────────────────────── */

function StepPrerequisites() {
    const reqs = [
        { icon: Cpu, label: 'Windows 10 / 11 (64-bit)', ok: true },
        { icon: Terminal, label: 'Python 3.11 installed', ok: true },
        { icon: Wifi, label: 'Internet connection', ok: true },
        { icon: Shield, label: 'Admin / elevated privileges', ok: true },
    ]
    return (
        <div className="space-y-3">
            <p className="text-slate-400 text-sm">
                Ensure the child's computer meets these requirements before proceeding.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3">
                {reqs.map(({ icon: Icon, label }) => (
                    <div key={label} className="flex items-center gap-3 bg-[#0a0d14] border border-[#1f3050] rounded-xl px-4 py-3">
                        <CheckCircle2 size={15} className="text-emerald-400 flex-shrink-0" />
                        <span className="text-slate-300 text-sm">{label}</span>
                    </div>
                ))}
            </div>
            <div className="flex items-start gap-3 bg-yellow-400/5 border border-yellow-400/20 rounded-xl px-4 py-3 mt-2">
                <AlertCircle size={15} className="text-yellow-400 flex-shrink-0 mt-0.5" />
                <p className="text-yellow-300 text-xs">
                    The agent must run as <strong>Administrator</strong> to pause internet and block applications.
                    Right-click → "Run as administrator" when launching.
                </p>
            </div>
        </div>
    )
}

function StepDownload() {
    const files = [
        { name: 'monitor.py', desc: 'Core monitoring agent', size: '18 KB' },
        { name: 'start_child_agent.bat', desc: 'One-click launcher (console)', size: '1 KB' },
        { name: 'start_silent.vbs', desc: 'Silent background launcher', size: '1 KB' },
        { name: 'install_autostart.vbs', desc: 'Auto-run on Windows startup', size: '2 KB' },
        { name: 'stop_monitoring.vbs', desc: 'Stop the agent gracefully', size: '1 KB' },
        { name: 'requirements.txt', desc: 'Python dependencies list', size: '1 KB' },
    ]
    return (
        <div className="space-y-4">
            <p className="text-slate-400 text-sm">
                Copy the <strong className="text-white">agent folder</strong> from the SafeNet installation
                to the child's computer — via USB drive, shared folder, or cloud storage.
            </p>
            <div className="space-y-2">
                {files.map(f => (
                    <div key={f.name} className="flex items-center gap-3 bg-[#0a0d14] border border-[#1f3050] rounded-xl px-4 py-2.5">
                        <span className="font-mono text-cyan-300 text-xs w-48 flex-shrink-0">{f.name}</span>
                        <span className="text-slate-500 text-xs flex-1">{f.desc}</span>
                        <Pill color="bg-slate-700/60 text-slate-400" text={f.size} />
                    </div>
                ))}
            </div>
            <div className="flex items-start gap-3 bg-cyan-400/5 border border-cyan-400/20 rounded-xl px-4 py-3">
                <BookOpen size={14} className="text-cyan-400 flex-shrink-0 mt-0.5" />
                <p className="text-cyan-300 text-xs">
                    Place the entire <code className="bg-[#0a0d14] px-1 rounded">agent/</code> folder in a permanent
                    location such as <code className="bg-[#0a0d14] px-1 rounded">C:\SafeNet\agent\</code> on the child's PC.
                </p>
            </div>
        </div>
    )
}

function StepInstall() {
    return (
        <div className="space-y-5">
            <p className="text-slate-400 text-sm">
                Open <strong className="text-white">Command Prompt as Administrator</strong> in the agent folder and run:
            </p>

            <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">① Install Python dependencies</p>
                <CodeBlock code={`cd C:\\SafeNet\\agent\npip install -r requirements.txt`} />
            </div>

            <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">② Set your Linking Code in the environment</p>
                <CodeBlock code={`set LINK_CODE=YOUR_CHILD_CODE_HERE`} />
                <p className="text-slate-500 text-xs mt-1">
                    (Replace with the code from <strong className="text-white">Settings → Add Child</strong>)
                </p>
            </div>

            <div>
                <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">③ Start the agent (choose one)</p>
                <div className="space-y-2">
                    <div className="flex items-center gap-3 bg-[#0a0d14] border border-[#1f3050] rounded-xl px-4 py-3">
                        <PlayCircle size={14} className="text-green-400 flex-shrink-0" />
                        <div className="flex-1">
                            <p className="text-white text-xs font-semibold">Console mode (visible terminal)</p>
                            <code className="text-cyan-300 text-xs">start_child_agent.bat</code>
                        </div>
                        <Pill color="bg-green-400/10 text-green-400" text="Recommended for testing" />
                    </div>
                    <div className="flex items-center gap-3 bg-[#0a0d14] border border-[#1f3050] rounded-xl px-4 py-3">
                        <Shield size={14} className="text-purple-400 flex-shrink-0" />
                        <div className="flex-1">
                            <p className="text-white text-xs font-semibold">Silent mode (hidden background process)</p>
                            <code className="text-cyan-300 text-xs">start_silent.vbs</code>
                        </div>
                        <Pill color="bg-purple-400/10 text-purple-400" text="Production use" />
                    </div>
                    <div className="flex items-center gap-3 bg-[#0a0d14] border border-[#1f3050] rounded-xl px-4 py-3">
                        <Monitor size={14} className="text-yellow-400 flex-shrink-0" />
                        <div className="flex-1">
                            <p className="text-white text-xs font-semibold">Auto-start on Windows boot</p>
                            <code className="text-cyan-300 text-xs">install_autostart.vbs</code>
                        </div>
                        <Pill color="bg-yellow-400/10 text-yellow-400" text="Run once to register" />
                    </div>
                </div>
            </div>
        </div>
    )
}

function StepLink() {
    return (
        <div className="space-y-4">
            <p className="text-slate-400 text-sm">
                The agent will ask for a <strong className="text-white">Linking Code</strong> on first run.
                Find yours in <strong className="text-white">Settings → Manage Children</strong>.
            </p>

            <div className="bg-[#0a0d14] border border-[#1f3050] rounded-2xl p-5 space-y-4">
                <div className="flex items-center gap-3 border-b border-[#1f3050] pb-4">
                    <div className="w-8 h-8 rounded-full bg-cyan-400/10 flex items-center justify-center text-cyan-400 font-black text-sm">1</div>
                    <div>
                        <p className="text-white text-sm font-semibold">Open parent dashboard → Settings</p>
                        <p className="text-slate-500 text-xs">Find your child's Linking Code shown next to their name</p>
                    </div>
                </div>
                <div className="flex items-center gap-3 border-b border-[#1f3050] pb-4">
                    <div className="w-8 h-8 rounded-full bg-cyan-400/10 flex items-center justify-center text-cyan-400 font-black text-sm">2</div>
                    <div>
                        <p className="text-white text-sm font-semibold">Enter code in the agent terminal</p>
                        <p className="text-slate-500 text-xs">The agent will prompt: <code className="text-cyan-300">Enter your Parent Linking Code:</code></p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-emerald-400/10 flex items-center justify-center text-emerald-400 font-black text-sm">3</div>
                    <div>
                        <p className="text-white text-sm font-semibold">Agent confirms: "Linked as [Child Name]"</p>
                        <p className="text-slate-500 text-xs">Monitoring begins immediately and the child appears Online in your dashboard</p>
                    </div>
                </div>
            </div>

            <div className="flex items-start gap-3 bg-cyan-400/5 border border-cyan-400/20 rounded-xl px-4 py-3">
                <Key size={14} className="text-cyan-400 flex-shrink-0 mt-0.5" />
                <p className="text-cyan-300 text-xs">
                    To skip the prompt, set <code className="bg-[#0a0d14] px-1 rounded">LINK_CODE=XXXXXX</code> in the system environment variables
                    or in the <code className="bg-[#0a0d14] px-1 rounded">.env</code> file before running.
                </p>
            </div>
        </div>
    )
}

function StepVerify() {
    const checks = [
        { label: 'Child shows 🟢 Online in the sidebar', detail: 'Heartbeat is reaching the server every 15 seconds' },
        { label: 'Dashboard shows activity logs', detail: 'Keyboard & browser activity should appear within minutes' },
        { label: 'Lock Device button works', detail: 'Go to Control Center → click Lock Device → child\'s screen should lock' },
        { label: 'Blocked site is enforced', detail: 'Add a test domain → open that site on child\'s browser → window should close' },
    ]
    return (
        <div className="space-y-4">
            <p className="text-slate-400 text-sm">
                Confirm everything is working correctly with these quick tests.
            </p>
            <div className="space-y-2">
                {checks.map((c, i) => (
                    <div key={i} className="flex items-start gap-3 bg-[#0a0d14] border border-[#1f3050] rounded-xl px-4 py-3">
                        <CheckCircle2 size={15} className="text-emerald-400 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-white text-sm font-medium">{c.label}</p>
                            <p className="text-slate-500 text-xs mt-0.5">{c.detail}</p>
                        </div>
                    </div>
                ))}
            </div>
            <div className="flex items-start gap-3 bg-emerald-400/5 border border-emerald-400/20 rounded-xl px-4 py-3">
                <CheckCircle2 size={14} className="text-emerald-400 flex-shrink-0 mt-0.5" />
                <p className="text-emerald-300 text-xs">
                    Once all checks pass, the child's device is fully monitored and controlled from this dashboard.
                    No further setup is needed.
                </p>
            </div>
        </div>
    )
}

/* ── Main Page ───────────────────────────────────────────────────── */

export default function SetupGuidePage() {
    const [activeStep, setActiveStep] = useState(1)

    const current = steps.find(s => s.id === activeStep)

    return (
        <div className="space-y-6 max-w-4xl">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-black text-white tracking-tight">Connect Child Device</h1>
                <p className="text-slate-500 text-sm mt-1">
                    Follow these steps to install the SafeNet monitoring agent on your child's computer
                </p>
            </div>

            {/* Architecture banner */}
            <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl px-5 py-4">
                <p className="text-slate-400 text-xs uppercase tracking-wider mb-3 font-semibold">How it works</p>
                <div className="flex items-center gap-2 flex-wrap">
                    {[
                        { label: 'Parent Dashboard', color: 'bg-cyan-400/10 text-cyan-400 border-cyan-400/20' },
                        null,
                        { label: 'Cloud API (Railway)', color: 'bg-purple-400/10 text-purple-400 border-purple-400/20' },
                        null,
                        { label: 'Child Agent (monitor.py)', color: 'bg-green-400/10 text-green-400 border-green-400/20' },
                        null,
                        { label: "Child's OS", color: 'bg-orange-400/10 text-orange-400 border-orange-400/20' },
                    ].map((item, i) =>
                        item === null
                            ? <ChevronRight key={i} size={14} className="text-slate-600" />
                            : <span key={i} className={`px-3 py-1.5 rounded-xl border text-xs font-semibold ${item.color}`}>{item.label}</span>
                    )}
                </div>
                <p className="text-slate-600 text-xs mt-3">
                    The parent controls via the website. The cloud API relays commands. The agent executes them on the child's device.
                </p>
            </div>

            {/* Step Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-1">
                {steps.map(step => {
                    const Icon = step.icon
                    const active = activeStep === step.id
                    return (
                        <button key={step.id} onClick={() => setActiveStep(step.id)}
                            className={`flex-shrink-0 flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-semibold transition ${active
                                ? `${step.bg} ${step.color} ${step.border}`
                                : 'bg-[#141d2e] border-[#1f3050] text-slate-400 hover:text-white hover:border-slate-500'
                                }`}>
                            <Icon size={14} />
                            <span className="hidden sm:inline">Step {step.id}:</span>
                            {step.title}
                        </button>
                    )
                })}
            </div>

            {/* Step Content Card */}
            {current && (
                <div className="bg-[#141d2e] border border-[#1f3050] rounded-2xl p-6">
                    <div className="flex items-center gap-4 mb-6">
                        <div className={`w-10 h-10 rounded-xl ${current.bg} border ${current.border} flex items-center justify-center`}>
                            <current.icon size={18} className={current.color} />
                        </div>
                        <div>
                            <h2 className="text-white font-bold text-lg leading-tight">{current.title}</h2>
                            <p className="text-slate-500 text-sm">{current.subtitle}</p>
                        </div>
                        <div className="ml-auto">
                            <Pill color="bg-slate-700/60 text-slate-400" text={`Step ${current.id} of ${steps.length}`} />
                        </div>
                    </div>

                    {current.content}

                    {/* Navigation */}
                    <div className="flex justify-between mt-6 pt-5 border-t border-[#1f3050]">
                        <button
                            disabled={activeStep === 1}
                            onClick={() => setActiveStep(s => s - 1)}
                            className="px-4 py-2 rounded-xl bg-[#1e2d45] border border-[#1f3050] text-slate-400 text-sm font-medium hover:text-white hover:border-slate-500 transition disabled:opacity-30 disabled:cursor-not-allowed">
                            ← Previous
                        </button>
                        {activeStep < steps.length ? (
                            <button
                                onClick={() => setActiveStep(s => s + 1)}
                                className="px-5 py-2 rounded-xl bg-cyan-400 text-black text-sm font-bold hover:opacity-90 transition flex items-center gap-2">
                                Next Step <ChevronRight size={14} />
                            </button>
                        ) : (
                            <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-400/10 border border-emerald-400/20 text-emerald-400 text-sm font-bold">
                                <CheckCircle2 size={14} /> Setup Complete!
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
