# Student Wellbeing & Triage Copilot — 4-Day Task Checklist

> **Total Timeline**: 4 Working Days  
> **Team**: Person 1, Person 2, Person 3  
> **Status**: Everything marked with **`[x]`** is **already completed and working in this repository**. Everything marked with **`[ ]`** is the work left to complete over the 4 days.

---

## 📅 DAY 1: Setup, Data & Basic Layout

### Person 1 (AI Safety & Triage)
- [x] Build pattern-matching engine to detect acute distress and self-harm language
- [x] Build rule-based safety engine that locks the session during a crisis
- [x] Implement emergency bypass: guarantee 0 calls to generative AI for crisis messages
- [x] Build emergency resource loader that returns crisis phone numbers (999, 988, Samaritans)
- [x] Build classifier to categorize non-crisis queries (academic, emotional, financial, admin)
- [x] Build core backend API (`/api/triage/analyze`)
- [x] Write automated test suite (107 tests passing)
- [x] Add real campus clinic phone numbers to `app/data/emergency_resources.json`
- [x] Create dummy/mock endpoints in FastAPI so Person 2 and Person 3 can test their code

### Person 2 (RAG & AI Assistant)
- [x] Collect 5 university policy documents (late submissions, mitigating circumstances, drop deadlines, fees, accommodations)
- [x] Collect 5 mental wellness & CBT resources (5-4-3-2-1 grounding, box breathing, sleep hygiene, exam anxiety)
- [x] Install ChromaDB (or FAISS)
- [x] Create two separate vector databases: one for **Policies** and one for **Wellness**

### Person 3 (Portal & Integration)
- [x] Create the React + Vite frontend project with Tailwind CSS
- [x] Build the main page layout with navigation tabs: (1) Chat, (2) Workload Planner, (3) Campus Resources
- [x] Add a top emergency button: *"In Crisis? Get 24/7 Immediate Help"*
- [x] Build a popup modal that displays emergency phone numbers when the top button is clicked

---

## 📅 DAY 2: Core AI, Chatbot & Syllabus Upload

### Person 1 (AI Safety & Triage)
- [x] Build a safety gatekeeper: check all incoming chat queries with the safety engine before passing them to Person 2's AI
- [x] Ensure that if a query is high-risk, the AI is immediately stopped and emergency contacts are returned
- [x] Add an audit log to record timestamps whenever crisis bypass is triggered (with personal text redacted)

### Person 2 (RAG & AI Assistant)
- [x] Split the collected policy and wellness documents into small text chunks
- [x] Generate embeddings and save them into the two ChromaDB databases
- [x] Connect the ChromaDB databases to Google Gemini (or OpenAI) to build the RAG chatbot
- [x] Instruct the AI via prompt to **always cite exact document names and section numbers** in answers
- [x] Create the backend chat endpoint (`/api/assistant/chat`)

### Person 3 (Portal & Integration)
- [x] Build the chat screen in React with user/assistant message bubbles
- [x] Add source citation badges (e.g., `[Source: Policy Handbook §4.2]`) under assistant messages
- [x] Add emergency lock: if a message is flagged as a crisis, lock the chat and display emergency phone cards
- [x] Build a syllabus upload box supporting PDF drag-and-drop and a "Paste Text" tab
- [x] Create the backend endpoint (`/api/agent/parse-syllabus`) to extract assignment names and dates

---

## 📅 DAY 3: Tasks, Email Drafter & Campus Directory

### Person 1 (AI Safety & Triage)
- [x] Create the campus directory backend endpoint (`/api/resources/campus`)
- [x] Add contact details for Financial Aid, Housing, and Disability Support
- [x] Add rate limiting and basic error handling so the server never crashes on bad input

### Person 2 (RAG & AI Assistant)
- [x] Build interactive CBT exercise endpoints (4-7-8 breathing timer, 5-4-3-2-1 grounding guide)
- [x] Add fallback check: if document similarity score is too low (< 0.60), tell student to contact a human advisor
- [x] Test chatbot against university questions to make sure citations are correct

### Person 3 (Portal & Integration)
- [x] Build the task scheduler: break big syllabus deadlines into daily 30-minute checklist items (Today / Tomorrow / Next Week)
- [x] Add interactive checkboxes so students can tick off completed study tasks
- [x] Build the *"Draft Extension Email"* button: generates a polite, formal email to the professor citing university policy with 1-click copy
- [x] Build the Campus Resource Directory page showing cards for Financial Aid, Housing, and Disability Support

---

## 📅 DAY 4: Testing, Hardening & Demo Preparation

### Person 1 (AI Safety & Triage)
- [x] Test the safety engine against tricky messages, slang, and jailbreak attempts to ensure the AI never leaks during a crisis
- [x] Run the full test suite (`pytest`) and verify everything passes with 0 errors
- [x] Document safety verification results for the presentation

### Person 2 (RAG & AI Assistant)
- [x] Check response speed: ensure chatbot replies in under 2.5 seconds
- [x] Pick and prepare 3 best demo questions with clear, verified citations (e.g., extenuating circumstances rule, exam panic grounding)
- [x] Prepare a simple diagram showing how the two knowledge bases work for the presentation

### Person 3 (Portal & Integration)
- [x] Polish frontend styling, animations, loading spinners, and error alerts
- [x] Connect all frontend buttons and forms to live backend APIs
- [ ] Record a 2-minute backup demo video (as safety against live Wi-Fi/projector issues)
- [ ] Rehearse the live walkthrough with Person 1 and Person 2:
  1. Triggering an emergency bypass (showing safety works)
  2. Asking a policy question (showing citation works)
  3. Uploading a syllabus (showing task breakdown and extension email drafter work)

---

## 📌 Summary of Roles
* **Person 1**: Safety Gatekeeper, Emergency Bypass, Risk Detection & Backend APIs 
* **Person 2**: Document Curation, ChromaDB Vector Store & Citation-Backed RAG Chatbot
* **Person 3**: React Frontend Dashboard, Syllabus Task Scheduler & Professor Extension Email Drafter
