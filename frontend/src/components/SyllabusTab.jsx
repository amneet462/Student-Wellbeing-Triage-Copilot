import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { 
  FileText, 
  UploadCloud, 
  Calendar, 
  CheckCircle2, 
  Clock, 
  Mail, 
  Copy, 
  Check, 
  Sparkles, 
  AlertCircle,
  ChevronRight,
  ListTodo,
  FileCheck,
  X,
  GraduationCap,
  Plus,
  Send,
  ExternalLink,
  ShieldCheck,
  CalendarDays,
  Loader2
} from 'lucide-react'

export default function SyllabusTab() {
  const [syllabusText, setSyllabusText] = useState('')
  const [activeInputMode, setActiveInputMode] = useState('paste') // 'paste' | 'upload'
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [parseError, setParseError] = useState('')
  const [activeTimeframe, setActiveTimeframe] = useState('all') // 'all' | 'today' | 'tomorrow' | 'next_week'
  const [newTaskInput, setNewTaskInput] = useState('')

  const [courseInfo, setCourseInfo] = useState({
    course_name: 'CS301: Advanced Algorithms & Data Structures',
    professor: {
      name: 'Prof. Evelyn Reed',
      email: 'evelyn.reed@university.edu',
      office: 'Turing Hall, Room 402'
    },
    assignments: [
      { title: 'Problem Set 3: Complexity Analysis', due_date: 'Nov 12, 2026', weight: '15%' },
      { title: 'Midterm Examination', due_date: 'Nov 20, 2026', weight: '25%' },
      { title: 'Research Project Submission & Codebase', due_date: 'Dec 02, 2026', weight: '40%' }
    ]
  })

  // Calendarized micro-tasks (Today / Tomorrow / Next Week)
  const [tasks, setTasks] = useState([
    {
      id: 1,
      title: 'Deconstruct rubric for Problem Set 3 and list 3 core deliverables (30 min)',
      assignment: 'Problem Set 3: Complexity Analysis',
      dueDate: 'Today (30m Sprint)',
      duration: '30 mins',
      timeframe: 'today',
      completed: true,
    },
    {
      id: 2,
      title: 'Gather primary lecture notes and create 1-page working skeleton for Problem Set 3 (30 min)',
      assignment: 'Problem Set 3: Complexity Analysis',
      dueDate: 'Today (Focus 2)',
      duration: '30 mins',
      timeframe: 'today',
      completed: false,
    },
    {
      id: 3,
      title: 'Draft the introductory thesis or solve Q1/Q2 for Problem Set 3 (45 min)',
      assignment: 'Problem Set 3: Complexity Analysis',
      dueDate: 'Tomorrow (Focus 1)',
      duration: '45 mins',
      timeframe: 'tomorrow',
      completed: false,
    },
    {
      id: 4,
      title: 'Conduct focused literature search and save 3 verified citations (30 min)',
      assignment: 'Problem Set 3: Complexity Analysis',
      dueDate: 'Tomorrow (Focus 2)',
      duration: '30 mins',
      timeframe: 'tomorrow',
      completed: false,
    },
    {
      id: 5,
      title: 'Perform peer-review check against grading rubric and proofread (30 min)',
      assignment: 'Problem Set 3: Complexity Analysis',
      dueDate: 'Next Week (Milestone 1)',
      duration: '30 mins',
      timeframe: 'next_week',
      completed: false,
    },
    {
      id: 6,
      title: 'Review lecture slide decks and prepare active recall flashcards for Midterm (30 min)',
      assignment: 'Midterm Examination',
      dueDate: 'Next Week (Milestone 2)',
      duration: '30 mins',
      timeframe: 'next_week',
      completed: false,
    },
  ])

  // Email Drafter Modal State
  const [emailModalOpen, setEmailModalOpen] = useState(false)
  const [copiedEmail, setCopiedEmail] = useState(false)
  const [isDraftingEmail, setIsDraftingEmail] = useState(false)
  const [emailError, setEmailError] = useState('')
  const [clipboardError, setClipboardError] = useState('')
  const [emailFormData, setEmailFormData] = useState({
    course_code: 'CS301',
    professor_name: 'Prof. Evelyn Reed',
    assignment_title: 'Problem Set 3: Complexity Analysis',
    due_date: 'Nov 12, 2026',
    reason: 'acute medical illness and migraine',
    requested_days: 3,
    student_name: 'Alex Morgan',
    student_id: '2026-8941'
  })
  const [draftedEmail, setDraftedEmail] = useState({
    subject: '',
    body: '',
    policy_cited: ''
  })
  const [professorEmail, setProfessorEmail] = useState('evelyn.reed@university.edu')

  const fileInputRef = useRef(null)

  const sampleSyllabus = `CS301: Advanced Algorithms & Data Structures (Spring 2026)
Instructor: Prof. Evelyn Reed (evelyn.reed@university.edu)
Office: Turing Hall, Room 402
Key Deadlines:
1. Problem Set 3: Complexity Analysis - Due Nov 12, 2026 (15%)
2. Midterm Examination - Nov 20, 2026 (25%)
3. Research Project Submission & Codebase - Due Dec 02, 2026 (40%)
Late Policy: 5% deduction per 24 hours up to 5 working days as per university academic regulations.`

  const handleLoadSample = () => {
    setSyllabusText(sampleSyllabus)
    setActiveInputMode('paste')
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSelectFile(e.target.files[0])
    }
  }

  const validateAndSelectFile = (file) => {
    const supportedFile = /\.(pdf|txt|md)$/i.test(file.name)
    if (!supportedFile) {
      setParseError('Choose a PDF, TXT, or Markdown syllabus file.')
      setSelectedFile(null)
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setParseError('The syllabus file must be 10 MB or smaller.')
      setSelectedFile(null)
      return
    }
    setParseError('')
    setSelectedFile(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelectFile(e.dataTransfer.files[0])
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  // Parse Syllabus & Generate Calendarized Micro-Tasks
  const handleDeescalate = async () => {
    if (activeInputMode === 'paste' && !syllabusText.trim()) return
    if (activeInputMode === 'upload' && !selectedFile) return

    setIsLoading(true)
    setParseError('')

    try {
      let res
      if (activeInputMode === 'upload' && selectedFile) {
        const formData = new FormData()
        formData.append('file', selectedFile)
        res = await axios.post('/api/agent/parse-syllabus', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } else {
        const formData = new FormData()
        formData.append('syllabus_text', syllabusText)
        res = await axios.post('/api/agent/parse-syllabus', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      }

      if (res.data) {
        const data = res.data
        if (data.course_name) {
          const parsedCourse = {
            course_name: data.course_name,
            professor: data.professor || { name: 'Course Instructor', email: 'instructor@university.edu' },
            assignments: data.assignments || []
          }
          setCourseInfo(parsedCourse)
          setProfessorEmail(parsedCourse.professor.email || '')

          // Pre-populate email modal with extracted info
          setEmailFormData((prev) => ({
            ...prev,
            course_code: data.course_name.split(':')[0] || 'CS301',
            professor_name: data.professor?.name || 'Prof. Reed',
            assignment_title: data.assignments?.[0]?.title || 'Coursework Assignment',
            due_date: data.assignments?.[0]?.due_date || 'Upcoming Deadline'
          }))
        }

        if (data.generated_tasks && data.generated_tasks.length > 0) {
          const mappedTasks = data.generated_tasks.map((gt, idx) => ({
            id: Date.now() + idx,
            title: gt.task,
            assignment: gt.assignment || (data.assignments && data.assignments[idx % data.assignments.length]?.title) || 'Course Deliverable',
            dueDate: gt.day,
            duration: `${gt.estimated_minutes || 30} mins`,
            timeframe: gt.timeframe || (idx < 2 ? 'today' : idx < 4 ? 'tomorrow' : 'next_week'),
            completed: false
          }))
          setTasks(mappedTasks)
        }
      }
    } catch (err) {
      console.error('Syllabus parser request failed:', err)
      setParseError('Could not parse the syllabus. Check the server connection and file format, then try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleTask = (id) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    )
  }

  const handleAddCustomTask = (e) => {
    e.preventDefault()
    if (!newTaskInput.trim()) return

    const newTask = {
      id: Date.now(),
      title: `${newTaskInput.trim()} (30 min)`,
      assignment: courseInfo.assignments[0]?.title || 'Coursework',
      dueDate: activeTimeframe === 'today' ? 'Today (Sprint)' : activeTimeframe === 'tomorrow' ? 'Tomorrow' : 'Next Week',
      duration: '30 mins',
      timeframe: activeTimeframe === 'all' ? 'today' : activeTimeframe,
      completed: false
    }

    setTasks((prev) => [newTask, ...prev])
    setNewTaskInput('')
  }

  // Request Extension Email Draft from Person 3's API
  const generateEmailDraft = async () => {
    setIsDraftingEmail(true)
    setEmailError('')
    try {
      const res = await axios.post('/api/agent/draft-email', emailFormData)
      if (res.data && res.data.status === 'success') {
        setDraftedEmail({
          subject: res.data.subject,
          body: res.data.body,
          policy_cited: res.data.policy_cited
        })
      } else {
        setEmailError('The email service returned an invalid response. Please try again.')
      }
    } catch (err) {
      console.error('Failed to draft email via API:', err)
      setEmailError('Could not generate the email draft. Check the server connection and try again.')
    } finally {
      setIsDraftingEmail(false)
    }
  }

  // Trigger initial email draft when opening modal
  const handleOpenEmailModal = () => {
    setEmailModalOpen(true)
    generateEmailDraft()
  }

  const copyEmailDraft = async () => {
    const fullText = `Subject: ${draftedEmail.subject}\n\n${draftedEmail.body}`
    setClipboardError('')
    try {
      await navigator.clipboard.writeText(fullText)
      setCopiedEmail(true)
      setTimeout(() => setCopiedEmail(false), 2200)
    } catch (err) {
      console.error('Failed to copy email draft:', err)
      setClipboardError('Clipboard access is unavailable. Select and copy the draft text instead.')
    }
  }

  // Filter tasks by active calendar timeframe
  const filteredTasks = tasks.filter((t) => {
    if (activeTimeframe === 'all') return true
    return t.timeframe === activeTimeframe
  })

  const completedCount = tasks.filter((t) => t.completed).length
  const progressPercent = Math.round((completedCount / Math.max(tasks.length, 1)) * 100)

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fadeIn">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-emerald-800 to-teal-700 text-white p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-emerald-200 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-emerald-300" />
            <span>Productivity Agent: Syllabus De-escalation & Scheduling</span>
          </div>
          <h2 className="text-2xl font-bold mt-1">
            Transform Heavy Deadlines into 30-Minute Micro-Actions
          </h2>
          <p className="text-emerald-100 text-sm mt-1 max-w-2xl">
            Overwhelmed by syllabus deadlines? Upload or paste your syllabus below to generate a calendarized
            30-minute daily action plan (Today, Tomorrow, Next Week) and draft policy-compliant professor extension requests in 1-click.
          </p>
        </div>

        <button
          onClick={handleOpenEmailModal}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white text-emerald-900 hover:bg-emerald-50 font-bold text-xs shadow-md transition-all self-start md:self-center"
        >
          <Mail className="w-4 h-4 text-emerald-700" />
          <span>Draft Professor Extension Email</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Syllabus Input */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-600" />
              <span>Syllabus Input</span>
            </h3>
            <button
              onClick={handleLoadSample}
              className="text-xs text-emerald-700 hover:text-emerald-800 font-semibold underline decoration-dotted"
            >
              Load Sample CS301
            </button>
          </div>

          <div className="flex p-1 bg-slate-100 rounded-lg text-xs font-medium">
            <button
              onClick={() => setActiveInputMode('paste')}
              className={`flex-1 py-1.5 rounded-md transition-colors ${
                activeInputMode === 'paste' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Paste Syllabus Text
            </button>
            <button
              onClick={() => setActiveInputMode('upload')}
              className={`flex-1 py-1.5 rounded-md transition-colors ${
                activeInputMode === 'upload' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Upload PDF / Doc
            </button>
          </div>

          {activeInputMode === 'paste' ? (
            <textarea
              rows={8}
              value={syllabusText}
              onChange={(e) => setSyllabusText(e.target.value)}
              placeholder="Paste course syllabus sections with assignment dates and grading policies..."
              className="w-full p-3 rounded-xl border border-slate-200 text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
            />
          ) : (
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                isDragging
                  ? 'border-emerald-500 bg-emerald-50/50 scale-[1.01]'
                  : selectedFile
                  ? 'border-emerald-400 bg-emerald-50/30'
                  : 'border-slate-200 hover:border-emerald-400 bg-slate-50/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md"
                onChange={handleFileChange}
                className="hidden"
              />

              {selectedFile ? (
                <div className="space-y-2">
                  <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                    <FileCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-800">{selectedFile.name}</p>
                    <p className="text-[11px] text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      setSelectedFile(null)
                    }}
                    className="inline-flex items-center gap-1 text-[11px] text-red-600 hover:text-red-700 font-semibold"
                  >
                    <X className="w-3 h-3" />
                    <span>Remove file</span>
                  </button>
                </div>
              ) : (
                <div>
                  <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                  <p className="text-xs font-semibold text-slate-700">
                    Click to browse or drag & drop syllabus PDF
                  </p>
                  <p className="text-[10px] text-slate-400 mt-1">
                    Supports PDF, TXT, MD up to 10MB
                  </p>
                </div>
              )}
            </div>
          )}

          <button
            onClick={handleDeescalate}
            disabled={isLoading || (activeInputMode === 'paste' && !syllabusText.trim()) || (activeInputMode === 'upload' && !selectedFile)}
            className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-sm transition-colors"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            <span>{isLoading ? 'Parsing Syllabus...' : 'De-escalate & Calendarize Micro-Tasks'}</span>
          </button>
          {parseError && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900" role="alert">
              {parseError}
            </div>
          )}

          {/* Extracted Course Overview Card */}
          {courseInfo && (
            <div className="pt-3 border-t border-slate-100 space-y-2.5">
              <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
                <GraduationCap className="w-4 h-4 text-emerald-600" />
                <span>{courseInfo.course_name}</span>
              </div>
              <div className="text-[11px] text-slate-600 flex items-center justify-between">
                <span>Instructor: {courseInfo.professor?.name}</span>
                <span className="font-mono text-slate-400">{courseInfo.professor?.email}</span>
              </div>

              {courseInfo.assignments && courseInfo.assignments.length > 0 && (
                <div className="space-y-1.5 pt-1">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Extracted Deliverables:
                  </p>
                  {courseInfo.assignments.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-50 border border-slate-100">
                      <span className="font-medium text-slate-700 truncate max-w-[200px]">{item.title}</span>
                      <div className="flex items-center gap-2 font-mono text-[11px]">
                        <span className="text-slate-500">{item.due_date}</span>
                        {item.weight && <span className="text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded font-bold">{item.weight}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Calendarized Micro-Task Checklist (Person 3 Day 3) */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                <ListTodo className="w-4 h-4 text-emerald-600" />
                <span>Calendarized Micro-Task Checklist</span>
              </h3>
              <p className="text-[11px] text-slate-500">
                {completedCount} of {tasks.length} micro-tasks completed ({progressPercent}%)
              </p>
            </div>

            {/* Progress Indicator */}
            <div className="flex items-center gap-3">
              <div className="w-28 bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <span className="text-xs font-bold text-emerald-700 font-mono">
                {progressPercent}%
              </span>
            </div>
          </div>

          {/* Calendarized Timeframe Filter Tabs (Today / Tomorrow / Next Week) */}
          <div className="flex p-1 bg-slate-100 rounded-xl text-xs font-semibold gap-1">
            {[
              { id: 'all', label: `All (${tasks.length})` },
              { id: 'today', label: `Today (${tasks.filter(t => t.timeframe === 'today').length})` },
              { id: 'tomorrow', label: `Tomorrow (${tasks.filter(t => t.timeframe === 'tomorrow').length})` },
              { id: 'next_week', label: `Next Week (${tasks.filter(t => t.timeframe === 'next_week').length})` },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTimeframe(tab.id)}
                className={`flex-1 py-1.5 rounded-lg transition-all ${
                  activeTimeframe === tab.id
                    ? 'bg-white text-emerald-800 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Quick Add Custom Micro-Task */}
          <form onSubmit={handleAddCustomTask} className="flex gap-2">
            <input
              type="text"
              value={newTaskInput}
              onChange={(e) => setNewTaskInput(e.target.value)}
              placeholder="Add an actionable 30-min study task (e.g., Read pages 40-55)..."
              className="flex-1 px-3 py-1.5 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
            />
            <button
              type="submit"
              className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center gap-1 shadow-xs transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          </form>

          {/* Checklist Items */}
          <div className="space-y-2.5 max-h-[460px] overflow-y-auto pr-1">
            {filteredTasks.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-400">
                No micro-tasks found for this timeframe.
              </div>
            ) : (
              filteredTasks.map((task) => (
                <div
                  key={task.id}
                  onClick={() => toggleTask(task.id)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-start gap-3 select-none ${
                    task.completed
                      ? 'bg-slate-50/80 border-slate-200 opacity-60'
                      : 'bg-white border-slate-200 hover:border-emerald-300 hover:shadow-sm'
                  }`}
                >
                  <div className="mt-0.5">
                    <CheckCircle2
                      className={`w-5 h-5 transition-colors ${
                        task.completed ? 'text-emerald-600 fill-emerald-100' : 'text-slate-300 hover:text-emerald-400'
                      }`}
                    />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <h4
                        className={`text-xs font-bold leading-snug ${
                          task.completed ? 'line-through text-slate-400' : 'text-slate-800'
                        }`}
                      >
                        {task.title}
                      </h4>
                      <span className="flex-shrink-0 flex items-center gap-1 text-[10px] font-mono font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
                        <Clock className="w-3 h-3" />
                        {task.duration}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 mt-1.5 text-[11px] text-slate-500">
                      <span className="font-medium text-slate-600 truncate max-w-[200px]">{task.assignment}</span>
                      <span>•</span>
                      <span className="text-emerald-700 font-semibold">{task.dueDate}</span>
                      <span className="ml-auto text-[10px] uppercase font-bold text-slate-400">
                        {task.timeframe.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Professor Extension Request Email Drafter Modal (Person 3 Day 3) */}
      {emailModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-emerald-100 text-emerald-700">
                  <Mail className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-base">
                    Extension Request Email Drafter
                  </h3>
                  <p className="text-xs text-slate-500 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Formatted under University Academic Regulations §4.3 (Extenuating Circumstances)</span>
                  </p>
                </div>
              </div>

              <button
                onClick={() => setEmailModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Editable Form Controls */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs">
              <div>
                <label className="block text-slate-500 font-semibold mb-1">Course Code</label>
                <input
                  type="text"
                  value={emailFormData.course_code}
                  onChange={(e) => setEmailFormData({ ...emailFormData, course_code: e.target.value })}
                  className="w-full p-1.5 bg-white rounded-lg border border-slate-200 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-500 font-semibold mb-1">Professor Name</label>
                <input
                  type="text"
                  value={emailFormData.professor_name}
                  onChange={(e) => setEmailFormData({ ...emailFormData, professor_name: e.target.value })}
                  className="w-full p-1.5 bg-white rounded-lg border border-slate-200 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-500 font-semibold mb-1">Professor Email</label>
                <input
                  type="email"
                  value={professorEmail}
                  onChange={(e) => setProfessorEmail(e.target.value)}
                  className="w-full p-1.5 bg-white rounded-lg border border-slate-200 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-500 font-semibold mb-1">Assignment Title</label>
                <input
                  type="text"
                  value={emailFormData.assignment_title}
                  onChange={(e) => setEmailFormData({ ...emailFormData, assignment_title: e.target.value })}
                  className="w-full p-1.5 bg-white rounded-lg border border-slate-200 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-500 font-semibold mb-1">Current Due Date</label>
                <input
                  type="text"
                  value={emailFormData.due_date}
                  onChange={(e) => setEmailFormData({ ...emailFormData, due_date: e.target.value })}
                  className="w-full p-1.5 bg-white rounded-lg border border-slate-200 text-xs"
                />
              </div>

              <div>
                <label className="block text-slate-500 font-semibold mb-1">Reason for Request</label>
                <select
                  value={emailFormData.reason}
                  onChange={(e) => setEmailFormData({ ...emailFormData, reason: e.target.value })}
                  className="w-full p-1.5 bg-white rounded-lg border border-slate-200 text-xs text-slate-700"
                >
                  <option value="acute medical illness and migraine">Acute Medical Illness & Migraine</option>
                  <option value="unexpected severe anxiety and mental health distress">Mental Health Crisis / Severe Anxiety</option>
                  <option value="bereavement and sudden family emergency">Family Emergency / Bereavement</option>
                  <option value="COVID-19 symptomatic infection and quarantine">COVID-19 / Infectious Illness</option>
                  <option value="hospitalization and urgent specialist treatment">Urgent Specialist Medical Care</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-500 font-semibold mb-1">Extension Days</label>
                <select
                  value={emailFormData.requested_days}
                  onChange={(e) => setEmailFormData({ ...emailFormData, requested_days: Number(e.target.value) })}
                  className="w-full p-1.5 bg-white rounded-lg border border-slate-200 text-xs text-slate-700"
                >
                  <option value={3}>3 Working Days (Standard)</option>
                  <option value={5}>5 Working Days (Extended)</option>
                  <option value={7}>7 Working Days (Major Disruption)</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                onClick={generateEmailDraft}
                disabled={isDraftingEmail}
                className="px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 rounded-lg text-xs font-semibold flex items-center gap-1.5 border border-emerald-200 transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                <span>{isDraftingEmail ? 'Regenerating...' : 'Regenerate Email Draft'}</span>
              </button>
            </div>

            {emailError && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900" role="alert">
                {emailError}
              </div>
            )}

            {/* Generated Email Preview Box */}
            <div className="bg-slate-900 text-slate-100 p-4 rounded-xl font-mono text-xs leading-relaxed max-h-72 overflow-y-auto whitespace-pre-wrap select-text border border-slate-800">
              <div className="text-emerald-400 font-bold mb-2 pb-2 border-b border-slate-800 flex items-center justify-between">
                <span>Subject: {draftedEmail.subject || (isDraftingEmail ? 'Generating draft...' : 'No draft available')}</span>
                <span className="text-[10px] text-slate-400 font-normal">
                  {isDraftingEmail ? 'Generating' : draftedEmail.body ? 'Ready to Review' : 'Not available'}
                </span>
              </div>
              {draftedEmail.body || 'The email draft will appear here after the API responds.'}
            </div>

            {/* Policy Citation Tag */}
            {draftedEmail.policy_cited && (
              <div className="text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200 flex items-center justify-between">
                <span>{draftedEmail.policy_cited}</span>
                <span className="text-emerald-700 font-semibold">Self-Certification Compliant</span>
              </div>
            )}
            {clipboardError && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900" role="alert">
                {clipboardError}
              </div>
            )}

            {/* Modal Actions */}
            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-slate-500">
                Tip: Submit this email and evidence prior to official submission time.
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setEmailModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
                >
                  Close
                </button>

                <a
                  href={`mailto:${encodeURIComponent(professorEmail.trim())}?subject=${encodeURIComponent(draftedEmail.subject)}&body=${encodeURIComponent(draftedEmail.body)}`}
                  aria-disabled={!draftedEmail.body}
                  onClick={(event) => {
                    if (!draftedEmail.body) event.preventDefault()
                  }}
                  className="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Open in Mail App</span>
                </a>

                <button
                  onClick={copyEmailDraft}
                  disabled={!draftedEmail.body || isDraftingEmail}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors"
                >
                  {copiedEmail ? (
                    <>
                      <Check className="w-4 h-4 text-emerald-200" />
                      <span>Copied to Clipboard!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      <span>1-Click Copy Email</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
