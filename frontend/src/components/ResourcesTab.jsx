import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { 
  Building2, 
  Phone, 
  Mail, 
  MapPin, 
  Clock, 
  ExternalLink, 
  Search, 
  HeartHandshake, 
  Coins, 
  GraduationCap, 
  Accessibility, 
  Home, 
  ShieldAlert 
} from 'lucide-react'

export default function ResourcesTab({ onTriggerEmergency }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const defaultResources = [
    {
      id: 'counselling-hub',
      title: 'Student Counselling & Mental Health Service',
      category: 'mental-health',
      icon: HeartHandshake,
      description: 'Free, confidential short-term psychological support, CBT therapy groups, and mental health advisor drop-ins.',
      phone: '0800 028 3766',
      email: 'counselling@university.ac.uk',
      location: 'Wellbeing Centre, Ground Floor, Student Union',
      hours: 'Mon-Fri 08:30 - 17:30 (Duty Triage Available Daily)',
      urgent: false,
    },
    {
      id: 'hardship-fund',
      title: 'Student Financial Aid & Emergency Hardship Fund',
      category: 'financial',
      icon: Coins,
      description: 'Non-repayable emergency grants for unexpected financial hardship, rent crises, and essential technology bursaries.',
      phone: '0800 456 1122',
      email: 'student.hardship@university.ac.uk',
      location: 'Student Hub, 2nd Floor, Senate House',
      hours: 'Mon-Thu 09:00 - 16:30 | Urgent appointments via triage',
      urgent: false,
    },
    {
      id: 'disability-service',
      title: 'Disability & Inclusion Support Service',
      category: 'disability',
      icon: Accessibility,
      description: 'Exam accommodations (25% extra time, rest breaks), assistive technology grants, and Learning Support Plans (LSP).',
      phone: '0800 789 3344',
      email: 'disability.inclusion@university.ac.uk',
      location: 'Library Wing B, Room 104',
      hours: 'Mon-Fri 09:00 - 17:00',
      urgent: false,
    },
    {
      id: 'academic-learning',
      title: 'Academic Skills & Writing Centre',
      category: 'academic',
      icon: GraduationCap,
      description: '1-on-1 consultations for dissertation structuring, time management strategies, and academic writing guidance.',
      phone: '0800 223 9911',
      email: 'academic.skills@university.ac.uk',
      location: 'Main University Library, Level 2',
      hours: 'Mon-Fri 10:00 - 18:00',
      urgent: false,
    },
    {
      id: 'housing-advice',
      title: 'Student Housing & Tenancy Support',
      category: 'housing',
      icon: Home,
      description: 'Advice on tenancy disputes, emergency short-stay campus rooms, and landlord dispute resolution.',
      phone: '0800 334 5566',
      email: 'housing.advice@university.ac.uk',
      location: 'Student Guild, North Campus',
      hours: 'Mon-Fri 09:30 - 16:00',
      urgent: false,
    },
    {
      id: 'campus-security',
      title: 'Campus 24/7 Safety & Security Operations',
      category: 'emergency',
      icon: ShieldAlert,
      description: '24/7 security dispatch, emergency medical first responders, and safe-walk campus escorts after dark.',
      phone: '0800 112 2334',
      email: 'security.control@university.ac.uk',
      location: 'Security Lodge, Main Gate (24/7)',
      hours: '24 Hours / 7 Days / 365 Days',
      urgent: true,
    }
  ]

  const categories = [
    { id: 'all', label: 'All Services' },
    { id: 'emergency', label: '24/7 Emergency' },
    { id: 'mental-health', label: 'Mental Health & CBT' },
    { id: 'financial', label: 'Hardship & Aid' },
    { id: 'disability', label: 'Disability & Inclusion' },
    { id: 'academic', label: 'Academic Skills' },
    { id: 'housing', label: 'Housing' },
  ]

  const filtered = defaultResources.filter((item) => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    const matchesSearch =
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.location.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-700 uppercase tracking-wider">
            <Building2 className="w-4 h-4" />
            <span>Campus Wellbeing & Institutional Resources</span>
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mt-1">
            Official University Support Directory
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Direct access to official university departments for mental health, financial hardship, disability accommodations, and security.
          </p>
        </div>

        <button
          onClick={onTriggerEmergency}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold text-xs shadow-sm shadow-red-500/30 transition-all self-start md:self-center"
        >
          <ShieldAlert className="w-4 h-4" />
          <span>View 24/7 Crisis Helplines</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by department name, services offered, or campus building location..."
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                selectedCategory === cat.id
                  ? 'bg-emerald-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200/70 hover:text-slate-900'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Directory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((item) => {
          const Icon = item.icon
          return (
            <div
              key={item.id}
              className={`p-5 rounded-2xl border bg-white shadow-sm flex flex-col justify-between transition-all hover:shadow-md ${
                item.urgent ? 'border-red-200 bg-red-50/20' : 'border-slate-200'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className={`p-2.5 rounded-xl ${item.urgent ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-700'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  {item.urgent && (
                    <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-red-100 text-red-700">
                      24/7 Priority
                    </span>
                  )}
                </div>

                <div>
                  <h3 className="font-bold text-slate-900 text-sm leading-snug">
                    {item.title}
                  </h3>
                  <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                    {item.description}
                  </p>
                </div>

                <div className="space-y-1.5 pt-2 border-t border-slate-100 text-[11px] text-slate-500">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    <span>{item.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    <span>{item.hours}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                <a
                  href={`tel:${item.phone.replace(/\s+/g, '')}`}
                  className="flex-1 py-1.5 px-3 rounded-lg bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Phone className="w-3.5 h-3.5" />
                  <span>{item.phone}</span>
                </a>

                <a
                  href={`mailto:${item.email}`}
                  className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors"
                  title="Send Email"
                >
                  <Mail className="w-4 h-4" />
                </a>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

