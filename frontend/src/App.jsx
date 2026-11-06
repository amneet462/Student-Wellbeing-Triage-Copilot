import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Navbar from './components/Navbar'
import EmergencyModal from './components/EmergencyModal'
import ChatTab from './components/ChatTab'
import SyllabusTab from './components/SyllabusTab'
import ResourcesTab from './components/ResourcesTab'

export default function App() {
  const [activeTab, setActiveTab] = useState('chat') // 'chat' | 'syllabus' | 'resources'
  const [isEmergencyOpen, setIsEmergencyOpen] = useState(false)
  const [backendStatus, setBackendStatus] = useState('connecting')

  useEffect(() => {
    // Check backend health status
    const checkBackend = async () => {
      try {
        const res = await axios.get('/api/triage/health', { timeout: 3000 })
        if (res.status === 200) {
          setBackendStatus('online')
        } else {
          setBackendStatus('degraded')
        }
      } catch (err) {
        // Fallback for standalone frontend development
        setBackendStatus('offline')
      }
    }

    checkBackend()
    const interval = setInterval(checkBackend, 15000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col selection:bg-emerald-100 selection:text-emerald-900">
      {/* Top Sticky Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenEmergency={() => setIsEmergencyOpen(true)}
        backendStatus={backendStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'chat' && (
          <ChatTab onTriggerEmergency={() => setIsEmergencyOpen(true)} />
        )}

        {activeTab === 'syllabus' && (
          <SyllabusTab />
        )}

        {activeTab === 'resources' && (
          <ResourcesTab onTriggerEmergency={() => setIsEmergencyOpen(true)} />
        )}
      </main>

      {/* Emergency Modal */}
      <EmergencyModal
        isOpen={isEmergencyOpen}
        onClose={() => setIsEmergencyOpen(false)}
      />

      {/* Institutional Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p>
            © 2026 Student Wellbeing & Triage Copilot • Built for Higher Education Safety
          </p>
          <div className="flex items-center gap-4 text-[11px] text-slate-400">
            <span>Deterministic Risk Detection</span>
            <span>•</span>
            <span>Dual-Store ChromaDB RAG</span>
            <span>•</span>
            <span>Zero-LLM Crisis Bypass Verified</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

