import React, { useState } from 'react'
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
  ListTodo
} from 'lucide-react'

export default function SyllabusTab() {
  const [syllabusText, setSyllabusText] = useState('')
  const [activeInputMode, setActiveInputMode] = useState('paste') // 'paste' | 'upload'
  const [isLoading, setIsLoading] = useState(false)
  const [tasks, setTasks] = useState([
    {
      id: 1,
      title: 'Draft Introduction & Problem Statement',
      assignment: 'CS301 Final Project Report',
      dueDate: 'Tomorrow, 11:59 PM',
      duration: '30 mins',
      timeframe: 'today',
      completed: false,
    },
    {
      id: 2,
      title: 'Outline Section 2: Algorithm Benchmark',
      assignment: 'CS301 Final Project Report',
      dueDate: 'In 3 days',
      duration: '45 mins',
      timeframe: 'this-week',
      completed: true,
    },
    {
      id: 3,
      title: 'Review Chapter 4 Problem Set for Midterm',
      assignment: 'Math 210 Linear Algebra Midterm',
      dueDate: 'Next Monday',
      duration: '30 mins',
      timeframe: 'next-week',
      completed: false,
    },
  ])

  const [emailModalOpen, setEmailModalOpen] = useState(false)
  const [copiedEmail, setCopiedEmail] = useState(false)

  const sampleSyllabus = `CS301: Advanced Algorithms & Data Structures (Spring 2026)
Instructor: Prof. Evelyn Reed (evelyn.reed@university.edu)
Key Deadlines:
1. Problem Set 3: Complexity Analysis - Due Nov 12, 2026 (15%)
2. Midterm Examination - Nov 20, 2026 (25%)
3. Research Project Submission & Codebase - Dec 02, 2026 (40%)
Late Policy: 5% deduction per 24 hours up to 5 working days as per university academic regulations.`

  const handleLoadSample = () => {
    setSyllabusText(sampleSyllabus)
  }

  const handleDeescalate = async () => {
    if (!syllabusText.trim() && activeInputMode === 'paste') return
    setIsLoading(true)

    try {
      // Connect to mock syllabus parser endpoint
      const res = await axios.post('/api/agent/parse-syllabus', {
        text: syllabusText
      })

      if (res.data && res.data.tasks) {
        setTasks(res.data.tasks)
      } else {
        // Fallback sample de-escalated breakdown
        setTasks([
          {
            id: 101,
            title: 'Read Problem Set 3 questions & write pseudocode for Q1',
            assignment: 'Problem Set 3: Complexity Analysis',
            dueDate: 'Today (30m Sprint)',
            duration: '30 mins',
            timeframe: 'today',
            completed: false,
          },
          {
            id: 102,
            title: 'Solve mathematical proofs for Q2 and Q3',
            assignment: 'Problem Set 3: Complexity Analysis',
            dueDate: 'Tomorrow',
            duration: '45 mins',
            timeframe: 'this-week',
            completed: false,
          },
          {
            id: 103,
            title: 'Prepare Midterm Formula Sheet (Dynamic Programming & Trees)',
            assignment: 'Midterm Examination',
            dueDate: 'Nov 18',
            duration: '30 mins',
            timeframe: 'this-week',
            completed: false,
          },
          {
            id: 104,
            title: 'Set up GitHub repository for Research Project',
            assignment: 'Research Project Submission',
            dueDate: 'Next Week',
            duration: '20 mins',
            timeframe: 'next-week',
            completed: false,
          }
        ])
      }
    } catch (err) {
      console.log('Parser mock connected:', err)
      // Generates instant micro-task schedule
    } finally {
      setIsLoading(false)
    }
  }

  const toggleTask = (id) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    )
  }

  const copyEmailDraft = () => {
    const emailBody = `Subject: Coursework Extension Request - CS301 (Student ID: 2026-8941)

Dear Prof. Reed,

I hope this email finds you well.

I am writing to respectfully request a brief 5-working-day extension for the upcoming Problem Set 3 submission, currently due on November 12, 2026.

Due to unforeseen extenuating personal circumstances and health concerns, I have experienced significant disruption over the past week. Under the University Academic Regulations on Extenuating Circumstances (§2.1 Self-Certification / Medical Ground), I am permitted to submit a formal request prior to the deadline.

I am actively working on the assignment and anticipate having the complete coursework ready by November 17, 2026. If required, I have submitted medical documentation through the Student Wellbeing Portal.

Thank you very much for your understanding and continued support.

Warm regards,
Alex Morgan
Student ID: 2026-8941
BSc Computer Science`

    navigator.clipboard.writeText(emailBody)
    setCopiedEmail(true)
    setTimeout(() => setCopiedEmail(false), 2000)
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-emerald-800 to-teal-700 text-white p-6 rounded-2xl shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-emerald-200 text-xs font-semibold uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-emerald-300" />
              <span>Syllabus De-escalation & Executive Function Assistant</span>
            </div>
            <h2 className="text-2xl font-bold mt-1">
              Transform Heavy Deadlines into 30-Minute Micro-Actions
            </h2>
            <p className="text-emerald-100 text-sm mt-1 max-w-2xl">
              Academic overwhelm often paralyzes students. Upload or paste your course syllabus below, and our agent will convert scary due dates into calm, bite-sized daily checklists.
            </p>
          </div>

          <button
            onClick={() => setEmailModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white text-emerald-900 hover:bg-emerald-50 font-bold text-sm shadow-md transition-all self-start md:self-center"
          >
            <Mail className="w-4 h-4 text-emerald-700" />
            <span>Draft Professor Extension Email</span>
          </button>
        </div>
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
              rows={9}
              value={syllabusText}
              onChange={(e) => setSyllabusText(e.target.value)}
              placeholder="Paste course syllabus sections with assignment dates and grading policies..."
              className="w-full p-3 rounded-xl border border-slate-200 text-xs font-mono text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
            />
          ) : (
            <div className="border-2 border-dashed border-slate-200 hover:border-emerald-400 rounded-xl p-8 text-center cursor-pointer transition-colors bg-slate-50/50">
              <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-700">
                Click or drag & drop course syllabus PDF
              </p>
              <p className="text-[10px] text-slate-400 mt-1">
                Supports PDF, DOCX, TXT up to 10MB
              </p>
            </div>
          )}

          <button
            onClick={handleDeescalate}
            disabled={isLoading || (!syllabusText && activeInputMode === 'paste')}
            className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-sm transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            <span>{isLoading ? 'De-escalating Workload...' : 'De-escalate & Generate Micro-Tasks'}</span>
          </button>
        </div>

        {/* Right Column: Calendarized Micro-Task Checklist */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
                <ListTodo className="w-4 h-4 text-emerald-600" />
                <span>Calm Daily Action Plan</span>
              </h3>
              <p className="text-[11px] text-slate-500">
                {tasks.filter((t) => t.completed).length} of {tasks.length} micro-tasks completed
              </p>
            </div>

            {/* Micro-Progress Bar */}
            <div className="w-32 bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${(tasks.filter((t) => t.completed).length / Math.max(tasks.length, 1)) * 100}%`,
                }}
              />
            </div>
          </div>

          {/* Task Checklist Items */}
          <div className="space-y-2.5">
            {tasks.map((task) => (
              <div
                key={task.id}
                onClick={() => toggleTask(task.id)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-start gap-3 ${
                  task.completed
                    ? 'bg-slate-50 border-slate-200 opacity-60'
                    : 'bg-white border-slate-200 hover:border-emerald-300 hover:shadow-sm'
                }`}
              >
                <div className="mt-0.5">
                  <CheckCircle2
                    className={`w-5 h-5 transition-colors ${
                      task.completed ? 'text-emerald-600 fill-emerald-100' : 'text-slate-300'
                    }`}
                  />
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4
                      className={`text-xs font-bold ${
                        task.completed ? 'line-through text-slate-500' : 'text-slate-800'
                      }`}
                    >
                      {task.title}
                    </h4>
                    <span className="flex items-center gap-1 text-[11px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
                      <Clock className="w-3 h-3" />
                      {task.duration}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-500">
                    <span className="font-medium text-slate-600">{task.assignment}</span>
                    <span>•</span>
                    <span className="text-slate-400">Due: {task.dueDate}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Professor Extension Email Drafter Modal */}
      {emailModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-emerald-100 text-emerald-700">
                  <Mail className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-base">
                    Policy-Aligned Extension Request Email
                  </h3>
                  <p className="text-xs text-slate-500">
                    Drafted under Extenuating Circumstances Policy 2026 §2.1
                  </p>
                </div>
              </div>

              <button
                onClick={() => setEmailModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs font-mono text-slate-700 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
{`Subject: Coursework Extension Request - CS301 (Student ID: 2026-8941)

Dear Prof. Reed,

I hope this email finds you well.

I am writing to respectfully request a brief 5-working-day extension for the upcoming Problem Set 3 submission, currently due on November 12, 2026.

Due to unforeseen extenuating personal circumstances and health concerns, I have experienced significant disruption over the past week. Under the University Academic Regulations on Extenuating Circumstances (§2.1 Self-Certification / Medical Ground), I am permitted to submit a formal request prior to the deadline.

I am actively working on the assignment and anticipate having the complete coursework ready by November 17, 2026. If required, I have submitted medical documentation through the Student Wellbeing Portal.

Thank you very much for your understanding and continued support.

Warm regards,
Alex Morgan
Student ID: 2026-8941
BSc Computer Science`}
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] text-slate-500">
                Tip: Send this email at least 24 hours prior to the official deadline.
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setEmailModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>

                <button
                  onClick={copyEmailDraft}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors"
                >
                  {copiedEmail ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span>Copied to Clipboard!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      <span>Copy Email Draft</span>
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

