import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  ShieldCheck, 
  ShieldAlert, 
  BookOpen, 
  Phone, 
  Lock, 
  Unlock, 
  RefreshCw, 
  ExternalLink,
  AlertTriangle,
  Heart,
  X,
  Clock,
  CheckCircle,
  Activity
} from 'lucide-react'

export default function ChatTab({ onTriggerEmergency }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: "Hello, I am your Student Wellbeing & Triage Copilot. I'm here to help you navigate academic regulations, deadline extensions, hardship funds, and CBT calming techniques. How are you feeling today?",
      category: 'general',
      riskLevel: 'low',
      citations: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isLocked, setIsLocked] = useState(false)
  const [crisisContacts, setCrisisContacts] = useState([])

  // CBT Grounding Exercises Modal State (Person 2 Day 3)
  const [cbtModalOpen, setCbtModalOpen] = useState(false)
  const [cbtExercises, setCbtExercises] = useState([])
  const [selectedCbtExercise, setSelectedCbtExercise] = useState(null)
  const [isLoadingCbt, setIsLoadingCbt] = useState(false)
  const [cbtError, setCbtError] = useState('')

  const defaultEmergencyContacts = [
    {
      name: 'Emergency Services (Police / Ambulance)',
      phone: '999',
      available: '24/7 Immediate',
      description: 'For immediate life-threatening danger or urgent medical emergencies.'
    },
    {
      name: 'Suicide & Crisis Lifeline',
      phone: '988',
      available: '24/7 Toll-Free',
      description: 'Free, confidential support for people in suicidal crisis or emotional distress.'
    },
    {
      name: 'Samaritans Helpline',
      phone: '116 123',
      available: '24/7 Confidential',
      description: 'Whatever you are going through, a Samaritan will face it with you.'
    },
    {
      name: 'Campus Security & Urgent First Aid',
      phone: '0800 123 4567',
      available: '24/7 On-Campus',
      description: 'Campus emergency response and rapid incident management.'
    }
  ]

  const quickPrompts = [
    { label: 'Request coursework extension', text: 'How do I apply for an extension for coursework due to illness?' },
    { label: 'Exam panic & breathing', text: 'I am having a panic attack before my exam, please help me calm down.' },
    { label: 'Emergency hardship aid', text: 'Where can I apply for emergency student hardship funds?' },
    { label: 'Disability accommodations', text: 'How do I request extra time accommodations for exams?' },
  ]

  // Fetch structured CBT exercises from Person 2's endpoint
  const loadCbtExercises = async () => {
    setIsLoadingCbt(true)
    setCbtError('')
    try {
      const res = await axios.get('/api/assistant/cbt-exercises')
      if (res.data && Array.isArray(res.data.exercises) && res.data.exercises.length > 0) {
        setCbtExercises(res.data.exercises)
        if (!selectedCbtExercise && res.data.exercises.length > 0) {
          setSelectedCbtExercise(res.data.exercises[0])
        }
      } else {
        setCbtError('The exercises service returned no exercises. Please try again.')
      }
    } catch (err) {
      console.error('Failed to load CBT exercises:', err)
      setCbtError('Could not load exercises. Check the server connection and try again.')
    } finally {
      setIsLoadingCbt(false)
    }
  }

  const handleOpenCbtModal = () => {
    setCbtModalOpen(true)
    if (cbtExercises.length === 0) {
      loadCbtExercises()
    }
  }

  const handleSend = async (textToSend) => {
    const query = (textToSend || inputText).trim()
    if (!query || isLoading || isLocked) return

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages((prev) => [...prev, userMsg])
    setInputText('')
    setIsLoading(true)

    try {
      // Send message to Assistant Chat endpoint protected by Safety Gatekeeper and Similarity Guard (< 0.60)
      const chatRes = await axios.post('/api/assistant/chat', {
        query: query,
        session_id: 'web-session-student-1'
      })

      const data = chatRes.data

      // Check if crisis was intercepted by the Safety Gatekeeper
      if (data.is_crisis) {
        setIsLocked(true)
        const contactsToUse = data.emergency_contacts && data.emergency_contacts.length > 0 
          ? data.emergency_contacts 
          : defaultEmergencyContacts
        setCrisisContacts(contactsToUse)
        if (onTriggerEmergency) onTriggerEmergency()

        const crisisMsg = {
          id: `crisis-${Date.now()}`,
          sender: 'assistant',
          text: data.reply || "⚠️ CRISIS DETECTED: Automated generative AI responses are locked for your safety. Please connect with human emergency support.",
          category: 'crisis',
          riskLevel: 'critical',
          citations: ['Clinical Safety Protocol: Zero-LLM Immediate Crisis Bypass'],
          isEmergency: true,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        setMessages((prev) => [...prev, crisisMsg])
        return
      }

      // Safe non-crisis response from RAG Assistant
      const citationsFormatted = (data.citations || []).map((c) => {
        if (typeof c === 'string') return c
        return `[Source: ${c.document} ${c.section || ''}]`.trim()
      })

      const assistantMsg = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: data.reply,
        category: data.fallback_suggested ? 'advisor fallback' : 'verified policy',
        riskLevel: 'low',
        fallbackSuggested: data.fallback_suggested,
        citations: citationsFormatted,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      console.error('Chat error:', err)
      const errorMsg = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: "I couldn't connect to the assistant service, so your message was not answered. Check the server connection and try again.",
        category: 'connection error',
        riskLevel: 'unknown',
        isError: true,
        citations: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-5xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden animate-fadeIn">
      {/* Chat Sub-header */}
      <div className="px-6 py-3.5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-800">
              Wellbeing & Policy Assistant
            </h2>
            <p className="text-[11px] text-slate-500">
              Powered by Dual-Store RAG • Fallback Guard (&lt;0.60) • AI Safety Gatekeeper
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* CBT Calming Exercises Button (Person 2 Day 3) */}
          <button
            onClick={handleOpenCbtModal}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 transition-colors shadow-2xs"
          >
            <Activity className="w-3.5 h-3.5 text-emerald-600" />
            <span>CBT Grounding Exercises</span>
          </button>

          {isLocked ? (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-red-100 text-red-800 border border-red-300 animate-pulse">
              <Lock className="w-3.5 h-3.5 text-red-600" />
              Emergency Lock Active
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Zero-LLM Safety Active
            </span>
          )}
        </div>
      </div>

      {/* Emergency Crisis Lockdown Banner */}
      {isLocked && (
        <div className="bg-red-50 border-b border-red-200 p-4 animate-fadeIn">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2 text-red-800 font-bold text-sm">
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <span>Session Locked: Clinical Safety Mode Active</span>
            </div>
            <button
              onClick={() => {
                setIsLocked(false)
                setCrisisContacts([])
              }}
              className="inline-flex items-center gap-1 text-xs px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-lg font-medium transition-colors"
            >
              <Unlock className="w-3 h-3 text-slate-600" />
              <span>Unlock Session (I am safe)</span>
            </button>
          </div>

          <p className="text-xs text-red-700 mb-3 leading-relaxed">
            Generative AI has been halted. If you or someone you know is in acute distress, please contact one of these free, confidential, 24/7 human resources immediately:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {(crisisContacts.length > 0 ? crisisContacts : defaultEmergencyContacts).map((c, i) => (
              <div key={i} className="bg-white p-3 rounded-xl border border-red-200 shadow-2xs flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-slate-800">{c.name}</h4>
                  <p className="text-[11px] text-slate-500">{c.available || '24/7 Available'}</p>
                </div>
                <a
                  href={`tel:${c.phone || '999'}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-xs"
                >
                  <Phone className="w-3.5 h-3.5" />
                  <span>{c.phone || '999'}</span>
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user'
          return (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold ${
                  isUser
                    ? 'bg-slate-800 text-white'
                    : msg.isEmergency
                    ? 'bg-red-600 text-white'
                    : 'bg-emerald-600 text-white shadow-sm'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : msg.isEmergency ? <ShieldAlert className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div className="space-y-1.5 max-w-[85%]">
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed ${
                    isUser
                      ? 'bg-slate-900 text-white rounded-tr-sm shadow-sm'
                      : msg.isEmergency
                      ? 'bg-red-50 border border-red-300 text-red-900 rounded-tl-sm font-medium'
                      : msg.isError
                      ? 'bg-amber-50 border border-amber-300 text-amber-900 rounded-tl-sm'
                      : msg.fallbackSuggested
                      ? 'bg-amber-50/80 text-amber-950 rounded-tl-sm border border-amber-200 shadow-sm'
                      : 'bg-slate-100 text-slate-800 rounded-tl-sm border border-slate-200/80 shadow-sm'
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.text}</p>
                </div>

                {/* Metadata & Source Citation Badges */}
                {!isUser && (
                  <div className="space-y-1.5 px-1">
                    <div className="flex items-center gap-2 text-[11px] text-slate-500">
                      <span>{msg.timestamp}</span>
                      <span>•</span>
                      <span className="capitalize font-medium text-slate-700">Status: {msg.category}</span>
                      {msg.fallbackSuggested && (
                        <>
                          <span>•</span>
                          <span className="text-amber-700 font-semibold bg-amber-100 px-1.5 py-0.5 rounded text-[10px]">
                            Human Advisor Recommended
                          </span>
                        </>
                      )}
                    </div>

                    {msg.citations && msg.citations.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-0.5">
                        {msg.citations.map((cite, i) => (
                          <span
                            key={i}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-[11px] font-semibold text-emerald-800 shadow-2xs"
                          >
                            <BookOpen className="w-3 h-3 text-emerald-600" />
                            {cite}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {isLoading && (
          <div className="flex gap-3 max-w-xl">
            <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="p-3.5 bg-slate-100 rounded-2xl rounded-tl-sm border border-slate-200 text-xs text-slate-500 flex items-center gap-2">
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-600" />
              <span>Checking safety gatekeeper and similarity threshold (&gt;0.60)...</span>
            </div>
          </div>
        )}
      </div>

      {/* Quick Prompts Bar */}
      {!isLocked && (
        <div className="px-6 py-2 bg-slate-50/80 border-t border-slate-200 flex items-center gap-2 overflow-x-auto">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex-shrink-0 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-500" />
            Suggested:
          </span>
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p.text)}
              className="flex-shrink-0 px-2.5 py-1 text-xs bg-white hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-300 text-slate-700 border border-slate-200 rounded-full transition-all duration-150"
            >
              {p.label}
            </button>
          ))}
        </div>
      )}

      {/* Input Form with Lock Guard */}
      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleSend()
        }}
        className="p-4 bg-white border-t border-slate-200 flex items-center gap-2"
      >
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={isLocked || isLoading}
          placeholder={
            isLocked
              ? "🔒 Chat is locked for clinical safety. Please connect with human crisis contacts above."
              : "Ask about extensions, late penalties, hardship funds, or CBT coping exercises..."
          }
          className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-500 text-sm placeholder-slate-400 disabled:bg-slate-50 disabled:text-slate-400"
        />
        <button
          type="submit"
          disabled={!inputText.trim() || isLoading || isLocked}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 active:scale-95 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold text-sm flex items-center gap-2 transition-all duration-150 shadow-sm"
        >
          <span>Send</span>
          <Send className="w-4 h-4" />
        </button>
      </form>

      {/* Interactive CBT Exercises Modal (Person 2 Day 3) */}
      {cbtModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-emerald-100 text-emerald-700">
                  <Activity className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-base">
                    Evidence-Based CBT & Somatic Grounding Exercises
                  </h3>
                  <p className="text-xs text-slate-500">
                    Somatic regulation and cognitive reframing tools (/api/assistant/cbt-exercises)
                  </p>
                </div>
              </div>

              <button
                onClick={() => setCbtModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Exercise Selector Buttons */}
            {isLoadingCbt && (
              <div className="flex items-center gap-2 text-xs text-slate-500" role="status">
                <RefreshCw className="w-4 h-4 animate-spin text-emerald-600" />
                Loading exercises...
              </div>
            )}
            {cbtError && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900" role="alert">
                <p>{cbtError}</p>
                <button
                  type="button"
                  onClick={loadCbtExercises}
                  className="mt-1 font-semibold underline"
                >
                  Retry
                </button>
              </div>
            )}
            <div className="flex gap-2 overflow-x-auto pb-1">
              {cbtExercises.map((ex) => (
                <button
                  key={ex.id}
                  onClick={() => setSelectedCbtExercise(ex)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors border ${
                    selectedCbtExercise?.id === ex.id
                      ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs'
                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {ex.name}
                </button>
              ))}
            </div>

            {/* Selected Exercise Detail */}
            {selectedCbtExercise && (
              <div className="space-y-3 p-4 bg-slate-50 rounded-xl border border-slate-200">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-900 text-sm">
                    {selectedCbtExercise.name}
                  </h4>
                  <span className="flex items-center gap-1 text-[11px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
                    <Clock className="w-3 h-3" />
                    {selectedCbtExercise.duration_min} minutes
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed italic bg-white p-2.5 rounded-lg border border-slate-200">
                  Clinical Rationale: {selectedCbtExercise.clinical_rationale}
                </p>

                {selectedCbtExercise.target_symptoms && selectedCbtExercise.target_symptoms.length > 0 && (
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Target Symptoms:</span>
                    {selectedCbtExercise.target_symptoms.map((sym, sIdx) => (
                      <span key={sIdx} className="text-[10px] bg-slate-200/70 text-slate-700 px-2 py-0.5 rounded-md">
                        {sym}
                      </span>
                    ))}
                  </div>
                )}

                <div className="space-y-2 pt-2">
                  <p className="text-xs font-bold text-slate-800">Sequential Action Steps:</p>
                  <ol className="space-y-1.5">
                    {selectedCbtExercise.steps.map((step, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs text-slate-700 bg-white p-2.5 rounded-lg border border-slate-100">
                        <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold flex items-center justify-center flex-shrink-0">
                          {idx + 1}
                        </span>
                        <span className="mt-0.5">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setCbtModalOpen(false)}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
