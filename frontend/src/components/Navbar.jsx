import React from 'react'
import { 
  HeartHandshake, 
  MessageSquareHeart, 
  CalendarClock, 
  Building2, 
  AlertTriangle, 
  PhoneCall, 
  Activity 
} from 'lucide-react'

export default function Navbar({ activeTab, setActiveTab, onOpenEmergency, backendStatus }) {
  const navTabs = [
    { id: 'chat', label: 'Triage & Wellbeing Chat', icon: MessageSquareHeart },
    { id: 'syllabus', label: 'Workload & Syllabus Planner', icon: CalendarClock },
    { id: 'resources', label: 'Campus Support Directory', icon: Building2 },
  ]

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200 shadow-sm">
      {/* Top Emergency Action Banner */}
      <div className="bg-slate-900 text-slate-100 px-4 py-2 text-xs flex flex-wrap items-center justify-between gap-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-medium text-[11px]">
            <AlertTriangle className="w-3 h-3" />
            Clinical Notice
          </span>
          <span className="text-slate-300">
            Automated student support tool. For life-threatening emergencies, call 999 (UK) or 988 (US) immediately.
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Backend Status indicator */}
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className={`w-2 h-2 rounded-full ${backendStatus === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`} />
            <span className="font-mono text-[11px]">Backend: {backendStatus}</span>
          </div>

          {/* Sticky Emergency Hotline Pill */}
          <button
            onClick={onOpenEmergency}
            className="flex items-center gap-1.5 px-3 py-1 bg-red-600 hover:bg-red-700 active:scale-95 text-white font-semibold rounded-full shadow-sm shadow-red-500/30 transition-all duration-150 animate-pulse"
          >
            <PhoneCall className="w-3.5 h-3.5" />
            <span>In Crisis? 24/7 Immediate Help</span>
          </button>
        </div>
      </div>

      {/* Main Brand & Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-3 gap-3">
          {/* Brand Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
              <HeartHandshake className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold text-slate-900 tracking-tight">
                  Student Wellbeing & Triage Copilot
                </h1>
                <span className="hidden md:inline-flex items-center px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md">
                  v1.0 Ready
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Safe AI Triage • University Policies RAG • CBT Somatic Grounding • Workload Management
              </p>
            </div>
          </div>

          {/* Tab Navigation Buttons */}
          <nav className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl border border-slate-200">
            {navTabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-white text-emerald-800 shadow-sm shadow-slate-200'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-600' : 'text-slate-400'}`} />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>
      </div>
    </header>
  )
}

