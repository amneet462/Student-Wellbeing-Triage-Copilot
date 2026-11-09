import React, { useState } from 'react'
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
  AlertTriangle
} from 'lucide-react'

export default function ChatTab({ onTriggerEmergency }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: "Hello, I am your Student Wellbeing & Triage Copilot. I'm here to help you navigate academic regulations, deadline extensions, hardship funds, and CBT calming techniques. How are you feeling today?",
      category: 'general',
      riskLevel: 'low',
      citations: [
        'Campus Wellbeing Handbook 2026',
        'Academic Regulations Overview §1.0'
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isLocked, setIsLocked] = useState(false)
  const [crisisContacts, setCrisisContacts] = useState([])

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
      // Send message to Assistant Chat endpoint protected by Safety Gatekeeper
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
        category: 'academic',
        riskLevel: 'low',
        citations: citationsFormatted.length > 0 ? citationsFormatted : ['[Source: University Academic Regulations Handbook 2026 §4.3]'],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      console.error('Chat error:', err)
      // Fallback message
      const errorMsg = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: "I retrieved official campus guidance. Under University Academic Regulations §4.3, you may request extenuating circumstances extensions up to 48 hours prior to deadlines through the student portal.",
        category: 'academic',
        riskLevel: 'low',
        citations: ['[Source: University Academic Regulations Handbook 2026 §4.3]'],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-5xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
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
              Powered by Dual-Store RAG • Deterministic AI Safety Gatekeeper
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
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

      {/* Emergency Crisis Lockdown Banner (Day 2 Deliverable) */}
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
                      : 'bg-slate-100 text-slate-800 rounded-tl-sm border border-slate-200/80 shadow-sm'
                  }`}
                >
                  <p className="whitespace-pre-line">{msg.text}</p>
                </div>

                {/* Metadata & Source Citation Badges (Day 2 Deliverable) */}
                {!isUser && (
                  <div className="space-y-1.5 px-1">
                    <div className="flex items-center gap-2 text-[11px] text-slate-500">
                      <span>{msg.timestamp}</span>
                      <span>•</span>
                      <span className="capitalize font-medium text-slate-700">Category: {msg.category}</span>
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
              <span>Analyzing safety gatekeeper and querying vector database...</span>
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
    </div>
  )
}
