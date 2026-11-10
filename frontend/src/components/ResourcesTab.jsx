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
<<<<<<< HEAD
  CheckCircle,
  Loader2,
=======
  AlertCircle,
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
  RefreshCw
} from 'lucide-react'

export default function ResourcesTab({ onTriggerEmergency }) {
  const [departments, setDepartments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('ALL')
  const [departments, setDepartments] = useState([])
  const [isLoading, setIsLoading] = useState(true)

<<<<<<< HEAD
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
=======
  const defaultResources = [
    {
      id: 'financial_aid',
      name: 'Student Financial Hardship & Emergency Bursary Desk',
      category: 'FINANCIAL',
      description: 'Emergency living bursaries, short-term interest-free crisis loans, food vouchers, and tuition fee instalment deferrals.',
      phone: '0800 028 4455',
      email: 'student.funding@university.ac.uk',
      office: 'Student Central Building, Ground Floor Suite 10',
      hours: 'Mon–Fri 9:00am–4:30pm',
      action_url: 'https://students.university.ac.uk/financial-aid',
      urgent_support: false,
    },
    {
      id: 'disability_services',
      name: 'Disability, Neurodiversity & Inclusion Team',
      category: 'DISABILITY',
      description: 'Reasonable exam adjustments, 25% extra time arrangements, assistive software licences, rest break passes, and sensory room access.',
      phone: '0800 028 7788',
      email: 'disability.support@university.ac.uk',
      office: 'Wilkins Building, Room 102',
      hours: 'Mon–Fri 8:30am–5:00pm',
      action_url: 'https://students.university.ac.uk/disability',
      urgent_support: false,
    },
    {
      id: 'emergency_housing',
      name: 'Student Housing Advisory & Emergency Shelter',
      category: 'HOUSING',
      description: 'Immediate emergency temporary shelter, private tenancy disputes, rent guarantor schemes, and deposit dispute resolution.',
      phone: '0800 028 9911',
      email: 'housing.advice@university.ac.uk',
      office: 'Campus Living Pavilion, Desk B',
      hours: '24/7 Crisis Dispatch & Weekdays 9:00am–5:00pm',
      action_url: 'https://students.university.ac.uk/housing',
      urgent_support: true,
    },
    {
      id: 'academic_advice',
      name: 'Student Union Independent Academic Advice',
      category: 'ACADEMIC',
      description: 'Confidential student advocacy, academic appeals, disciplinary hearing representation, and course withdrawal/deferral guidance.',
      phone: '0800 028 3344',
      email: 'academic.advice@su.university.ac.uk',
      office: 'Student Union Building, Floor 1',
      hours: 'Mon–Fri 9:30am–4:00pm',
      action_url: 'https://su.university.ac.uk/advice',
      urgent_support: false,
    },
    {
      id: 'mental_health_hub',
      name: 'Student Mental Health & Psychological Wellbeing Hub',
      category: 'WELLNESS',
      description: 'Free short-term CBT counselling, structured anxiety workshops, guided somatic meditation sessions, and duty clinician drop-ins.',
      phone: '0800 028 3766',
      email: 'counselling.hub@university.ac.uk',
      office: 'Wellbeing Centre, Ground Floor',
      hours: 'Mon–Fri 8:30am–5:30pm (Same-day duty triage appointments daily)',
      action_url: 'https://students.university.ac.uk/wellbeing',
      urgent_support: true,
    },
    {
      id: 'campus_security',
      name: 'Campus 24/7 Safety, Security & First Response',
      category: 'SECURITY',
      description: '24/7 rapid security dispatch, emergency medical first responders, defibrillator access, and night-time safe-walk campus escorts.',
      phone: '0800 112 2334',
      email: 'security.control@university.ac.uk',
      office: 'Main Gatehouse & Security Operations Pavilion',
      hours: '24 Hours / 7 Days / 365 Days a Year',
      action_url: 'https://students.university.ac.uk/security',
      urgent_support: true,
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
    }
  }

  useEffect(() => {
    fetchCampusDirectory(selectedCategory)
  }, [selectedCategory])

  const categoryIcons = {
    FINANCIAL: Coins,
    DISABILITY: Accessibility,
    HOUSING: Home,
    ACADEMIC: GraduationCap,
    WELLNESS: HeartHandshake,
    SECURITY: ShieldAlert,
  }

  const categories = [
<<<<<<< HEAD
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
=======
    { id: 'ALL', label: 'All Services' },
    { id: 'FINANCIAL', label: 'Financial Aid' },
    { id: 'DISABILITY', label: 'Disability & Inclusion' },
    { id: 'HOUSING', label: 'Housing' },
    { id: 'ACADEMIC', label: 'Academic Advice' },
    { id: 'WELLNESS', label: 'Mental Health' },
    { id: 'SECURITY', label: 'Security & Safety' },
  ]

  useEffect(() => {
    const fetchResources = async () => {
      setIsLoading(true)
      try {
        const params = {}
        if (selectedCategory !== 'ALL') {
          params.category = selectedCategory
        }
        if (searchQuery.trim()) {
          params.q = searchQuery.trim()
        }
        const res = await axios.get('/api/resources/campus', { params })
        if (res.data && res.data.departments) {
          setDepartments(res.data.departments)
        } else {
          setDepartments(defaultResources)
        }
      } catch (err) {
        console.error('Failed to fetch campus directory:', err)
        // Fallback to local resources
        let filtered = defaultResources
        if (selectedCategory !== 'ALL') {
          filtered = filtered.filter(d => d.category === selectedCategory)
        }
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase()
          filtered = filtered.filter(d => 
            d.name.toLowerCase().includes(q) || 
            d.description.toLowerCase().includes(q) ||
            d.office.toLowerCase().includes(q)
          )
        }
        setDepartments(filtered)
      } finally {
        setIsLoading(false)
      }
    }

    const timeout = setTimeout(fetchResources, 200)
    return () => clearTimeout(timeout)
  }, [selectedCategory, searchQuery])
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad

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
<<<<<<< HEAD
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
=======
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 flex items-center justify-center gap-2">
          <RefreshCw className="w-5 h-5 animate-spin text-emerald-600" />
          <span className="text-sm font-medium">Loading university directory...</span>
        </div>
      ) : departments.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 space-y-2">
          <AlertCircle className="w-8 h-8 text-slate-400 mx-auto" />
          <p className="text-sm font-semibold text-slate-700">No departments match your search.</p>
          <p className="text-xs text-slate-400">Try adjusting your category or search terms.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {departments.map((item) => {
            const Icon = categoryIcons[item.category] || Building2
            return (
              <div
                key={item.id}
                className={`p-5 rounded-2xl border bg-white shadow-sm flex flex-col justify-between transition-all hover:shadow-md ${
                  item.urgent_support ? 'border-red-200 bg-red-50/20' : 'border-slate-200'
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className={`p-2.5 rounded-xl ${item.urgent_support ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-700'}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    {item.urgent_support && (
                      <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-red-100 text-red-700">
                        Priority Service
                      </span>
                    )}
                  </div>

                  <div>
                    <h3 className="font-bold text-slate-900 text-sm leading-snug">
                      {item.name}
                    </h3>
                    <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                      {item.description}
                    </p>
                  </div>

                  <div className="space-y-1.5 pt-2 border-t border-slate-100 text-[11px] text-slate-500">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                      <span>{item.office}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                      <span>{item.hours}</span>
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
                    </div>
                  </div>
                </div>

<<<<<<< HEAD
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
=======
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
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
                  >
                    <Mail className="w-4 h-4" />
                  </a>

<<<<<<< HEAD
                  {dept.action_url && (
                    <a
                      href={dept.action_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="py-2 px-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
                    >
                      <span>Portal</span>
                      <ExternalLink className="w-3.5 h-3.5" />
=======
                  {item.action_url && (
                    <a
                      href={item.action_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition-colors"
                      title="Visit Portal"
                    >
                      <ExternalLink className="w-4 h-4" />
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
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
