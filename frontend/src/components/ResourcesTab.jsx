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
  ShieldAlert,
  CheckCircle,
  Loader2,
  RefreshCw
} from 'lucide-react'

export default function ResourcesTab({ onTriggerEmergency }) {
  const [departments, setDepartments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const categoryIcons = {
    FINANCIAL: Coins,
    DISABILITY: Accessibility,
    HOUSING: Home,
    ACADEMIC: GraduationCap,
    GENERAL: HeartHandshake,
  }

  const fetchCampusDirectory = async (cat = 'all') => {
    setIsLoading(true)
    setError(null)
    try {
      const url = cat === 'all' 
        ? '/api/resources/campus' 
        : `/api/resources/campus?category=${encodeURIComponent(cat)}`
      const res = await axios.get(url)
      if (res.data && res.data.departments) {
        setDepartments(res.data.departments)
      } else {
        setDepartments([])
      }
    } catch (err) {
      console.error('Failed to fetch campus directory:', err)
      setError('Unable to connect to Campus Directory service. Please check server status.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchCampusDirectory(selectedCategory)
  }, [selectedCategory])

  const categories = [
    { id: 'all', label: 'All Departments' },
    { id: 'financial', label: 'Financial Aid & Hardship' },
    { id: 'accommodations', label: 'Accommodations & Disability' },
    { id: 'housing', label: 'Emergency Housing' },
    { id: 'academic', label: 'Academic Advocacy' },
  ]

  const filteredDepartments = departments.filter((dept) => {
    const query = searchQuery.toLowerCase().trim()
    if (!query) return true
    return (
      dept.name.toLowerCase().includes(query) ||
      dept.description.toLowerCase().includes(query) ||
      dept.office.toLowerCase().includes(query) ||
      (dept.services && dept.services.some((s) => s.toLowerCase().includes(query)))
    )
  })

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white p-6 rounded-2xl shadow-sm border border-slate-700 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-wider">
            <Building2 className="w-4 h-4" />
            <span>Official University Support Directory (Person 1 API)</span>
          </div>
          <h2 className="text-2xl font-bold mt-1 text-white">
            Campus Department Support Directory
          </h2>
          <p className="text-sm text-slate-300 mt-1 max-w-2xl">
            Directly connect with Financial Aid, Disability Accommodations, Housing Advisory, and Academic Support.
            Protects student wellbeing and routes non-clinical inquiries directly to specialist departments.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start md:self-center">
          <button
            onClick={() => fetchCampusDirectory(selectedCategory)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
            title="Refresh directory"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Sync</span>
          </button>

          <button
            onClick={onTriggerEmergency}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-semibold text-xs shadow-md shadow-red-500/20 transition-all"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>View 24/7 Crisis Helplines</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by department name, services offered (e.g. bursary, 25% extra time, safe shelter), or office location..."
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-slate-800"
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

      {/* Loading state */}
      {isLoading && (
        <div className="bg-white p-12 rounded-2xl border border-slate-200 flex flex-col items-center justify-center space-y-3">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin" />
          <p className="text-xs font-semibold text-slate-600">Connecting to /api/resources/campus...</p>
        </div>
      )}

      {/* Error state */}
      {error && !isLoading && (
        <div className="bg-amber-50 p-6 rounded-2xl border border-amber-200 text-amber-900 space-y-2">
          <p className="text-sm font-bold flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            <span>Connection Notice</span>
          </p>
          <p className="text-xs text-amber-800">{error}</p>
          <button
            onClick={() => fetchCampusDirectory(selectedCategory)}
            className="mt-2 px-3 py-1.5 bg-amber-600 text-white rounded-lg text-xs font-semibold hover:bg-amber-700 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Directory Grid */}
      {!isLoading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {filteredDepartments.map((dept) => {
            const IconComponent = categoryIcons[dept.category] || Building2
            return (
              <div
                key={dept.id}
                className="p-6 rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col justify-between hover:border-emerald-300 hover:shadow-md transition-all space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="p-3 rounded-xl bg-emerald-50 text-emerald-700">
                      <IconComponent className="w-6 h-6" />
                    </div>
                    <span className="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200">
                      {dept.category}
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-slate-900 text-base leading-snug">
                      {dept.name}
                    </h3>
                    <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                      {dept.description}
                    </p>
                  </div>

                  {/* Key Services Offered */}
                  {dept.services && dept.services.length > 0 && (
                    <div className="pt-2">
                      <p className="text-[11px] font-bold text-slate-700 mb-1.5 uppercase tracking-wide">
                        Services & Support:
                      </p>
                      <ul className="space-y-1">
                        {dept.services.map((svc, sIdx) => (
                          <li key={sIdx} className="flex items-start gap-1.5 text-xs text-slate-600">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                            <span>{svc}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="space-y-1.5 pt-3 border-t border-slate-100 text-xs text-slate-600">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                      <span>{dept.office}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                      <span>{dept.hours}</span>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <a
                    href={`tel:${dept.phone.replace(/\s+/g, '')}`}
                    className="flex-1 py-2 px-3 rounded-xl bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Phone className="w-3.5 h-3.5" />
                    <span>{dept.phone}</span>
                  </a>

                  <a
                    href={`mailto:${dept.email}`}
                    className="p-2 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors"
                    title={`Email ${dept.name}`}
                  >
                    <Mail className="w-4 h-4" />
                  </a>

                  {dept.action_url && (
                    <a
                      href={dept.action_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="py-2 px-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
                    >
                      <span>Portal</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
