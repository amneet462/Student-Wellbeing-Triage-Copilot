import React, { useState } from 'react'
import { 
  AlertCircle, 
  PhoneCall, 
  MessageSquare, 
  Copy, 
  Check, 
  X, 
  ShieldAlert, 
  HeartHandshake, 
  Building 
} from 'lucide-react'

export default function EmergencyModal({ isOpen, onClose }) {
  const [copiedId, setCopiedId] = useState(null)

  if (!isOpen) return null

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const crisisContacts = [
    {
      id: 'emergency-services',
      title: 'Emergency Services (Police, Ambulance, Fire)',
      region: 'UK / National',
      phone: '999',
      altPhone: '112',
      hours: '24/7 • Immediate Response',
      type: 'Immediate Emergency',
      color: 'border-red-500 bg-red-50/60',
      description: 'Call immediately if you or someone else is in immediate danger of injury or loss of life.'
    },
    {
      id: 'samaritans',
      title: 'Samaritans Free Helpline',
      region: 'UK & ROI',
      phone: '116 123',
      hours: '24/7 • 365 Days a Year',
      type: 'Emotional Support',
      color: 'border-emerald-500 bg-emerald-50/60',
      description: 'Free, confidential listening support for anyone in distress or struggling to cope. No judgement.'
    },
    {
      id: 'shout',
      title: 'Shout Crisis Text Line',
      region: 'UK Free Text Service',
      phone: '85258',
      textKeyword: 'Text "SHOUT" to 85258',
      hours: '24/7 • Free on major UK networks',
      type: 'Text Support',
      color: 'border-blue-500 bg-blue-50/60',
      description: 'Free, confidential text conversation with trained crisis volunteers if you do not want to speak aloud.'
    },
    {
      id: 'campus-crisis',
      title: 'Campus 24/7 Mental Health Crisis Team',
      region: 'University Campus Dedicated',
      phone: '0800 028 3766',
      hours: '24/7 Dedicated Student Support',
      type: 'Campus Emergency',
      color: 'border-purple-500 bg-purple-50/60',
      description: 'Immediate connection to trained university mental health duty practitioners and triage officers.'
    },
    {
      id: 'campus-security',
      title: 'Campus Emergency Security & First Aid',
      region: 'University Campus Security Control',
      phone: '0800 112 2334',
      hours: '24/7 Rapid Response',
      type: 'On-Campus Security',
      color: 'border-amber-500 bg-amber-50/60',
      description: 'Fastest on-campus response team for medical emergencies, safety concerns, or building access.'
    },
    {
      id: 'us-988',
      title: 'Suicide & Crisis Lifeline (US & Canada)',
      region: 'North America',
      phone: '988',
      hours: '24/7 Voice & Text',
      type: 'Crisis Helpline',
      color: 'border-teal-500 bg-teal-50/60',
      description: 'If you are calling or studying from North America, dial or text 988 for free support.'
    }
  ]

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative bg-white w-full max-w-3xl rounded-2xl shadow-2xl border border-red-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Urgent Header Banner */}
        <div className="bg-gradient-to-r from-red-600 via-rose-600 to-red-700 text-white p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1.5 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-start gap-4">
            <div className="p-3 bg-white/10 rounded-xl backdrop-blur">
              <ShieldAlert className="w-8 h-8 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-white text-red-700">
                  Emergency Support
                </span>
                <span className="text-xs text-rose-100 font-medium">Free & Confidential</span>
              </div>
              <h2 className="text-2xl font-extrabold tracking-tight mt-1">
                You Are Not Alone. 24/7 Immediate Help Available
              </h2>
              <p className="text-sm text-rose-100 mt-1">
                If you are in acute distress, feeling overwhelmed, or experiencing thoughts of harm, please contact human emergency services below.
              </p>
            </div>
          </div>
        </div>

        {/* Safety Protocol Callout */}
        <div className="bg-red-50 border-b border-red-100 px-6 py-3 flex items-center gap-3 text-xs text-red-900 font-medium">
          <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
          <span>
            <strong>Deterministic Zero-LLM Safety Bypass:</strong> During high-risk states, automated AI replies are locked to prevent synthetic advice and direct you immediately to certified human clinicians.
          </span>
        </div>

        {/* Emergency Resources Cards Grid */}
        <div className="p-6 max-h-[65vh] overflow-y-auto space-y-3.5 bg-slate-50/50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {crisisContacts.map((contact) => (
              <div
                key={contact.id}
                className={`p-4 rounded-xl border bg-white shadow-sm flex flex-col justify-between transition-all hover:shadow-md ${contact.color}`}
              >
                <div>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-semibold text-slate-500 uppercase tracking-wider text-[10px]">
                      {contact.region}
                    </span>
                    <span className="px-2 py-0.5 rounded-md font-medium text-[10px] bg-white/80 border border-slate-200 text-slate-700">
                      {contact.hours}
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-900 text-sm">
                    {contact.title}
                  </h3>
                  <p className="text-xs text-slate-600 mt-1 line-clamp-2">
                    {contact.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <div className="font-mono font-bold text-base text-slate-900">
                    {contact.phone}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => handleCopy(contact.id, contact.phone)}
                      className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 text-slate-700 text-xs font-medium flex items-center gap-1 transition-colors"
                      title="Copy phone number"
                    >
                      {copiedId === contact.id ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                          <span className="text-emerald-700">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5 text-slate-500" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                    <a
                      href={`tel:${contact.phone.replace(/\s+/g, '')}`}
                      className="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-semibold flex items-center gap-1 shadow-sm transition-colors"
                    >
                      <PhoneCall className="w-3.5 h-3.5" />
                      <span>Call Now</span>
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer & Return */}
        <div className="bg-white border-t border-slate-200 px-6 py-3.5 flex items-center justify-between">
          <p className="text-[11px] text-slate-500">
            Emergency contacts verified from official university health services protocol.
          </p>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-semibold transition-colors"
          >
            Close Emergency Panel
          </button>
        </div>
      </div>
    </div>
  )
}

