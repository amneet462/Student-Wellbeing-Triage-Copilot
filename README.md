# AI-Powered Student Wellbeing & Triage Copilot
## Student-Wellbeing-Triage-Copilot

This project is an AI-powered student support assistant that helps students deal with academic stress, mental health concerns, and university-related problems without having to wait for a counselling appointment.

## Module 1: AI Safety & Risk Triage Engine

> ⚠️ **Clinical Disclaimer**: This system provides automated initial triage support only. It does not diagnose mental health conditions, guarantee crisis detection, or replace professional clinical assessment. If you are in immediate danger, please call your local emergency services.

---

## Overview

Module 1 is the safety backbone of the Student Wellbeing Copilot. It is responsible for:

- **Analysing** student messages for risk indicators
- **Classifying** messages into issue categories
- **Routing** non-crisis messages to the correct downstream module (Module 2 or 3)
- **Triggering emergency bypass** for critical messages — immediately stopping any generative AI workflow and returning pre-configured emergency contacts

---

## Project Structure

```
student-wellbeing-triage/
│
├── app/
│   ├── main.py                      ← FastAPI app entry point
│   ├── config.py                    ← All configuration (env-driven)
│   │
│   ├── api/
│   │   └── triage_routes.py         ← API endpoint definitions
│   │
│   ├── services/
│   │   ├── risk_detector.py         ← Two-layer risk detection engine
│   │   ├── category_classifier.py   ← Issue category classifier
│   │   ├── emergency_handler.py     ← Emergency resource loader (no LLM)
│   │   └── resource_router.py       ← Deterministic routing decisions
│   │
│   ├── orchestration/
│   │   └── state_machine.py         ← Deterministic triage state machine
│   │
│   ├── schemas/
│   │   └── triage_schema.py         ← Pydantic request/response models
│   │
│   └── data/
│       └── emergency_resources.json ← Admin-configurable emergency contacts
│
├── tests/
│   ├── test_risk_detection.py       ← Risk detector unit tests
│   ├── test_emergency_bypass.py     ← Emergency bypass tests (incl. LLM=0 proof)
│   ├── test_state_machine.py        ← State machine unit tests
│   └── test_api.py                  ← API integration tests
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- pip

### 2. Clone / Navigate to the project directory

```bash
cd StudentWellbeingtriage
```

### 3. Create and activate a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment

```bash
copy .env.example .env
# Edit .env with your university ID and settings
```

### 6. Configure emergency resources

> **IMPORTANT**: Before deploying to production, open `app/data/emergency_resources.json` and replace all entries marked `"verified": false` with your institution's actual contact details. Never deploy with placeholder values.

### 7. Run the server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Access the API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/api/triage/health

---

## Running Tests

```bash
pytest tests/ -v
```

To run a specific test file:

```bash
pytest tests/test_emergency_bypass.py -v
```

To see the LLM=0 proof test specifically:

```bash
pytest tests/test_emergency_bypass.py::TestEmergencyBypass::test_llm_invocation_count_is_zero_for_critical -v
```

---

## API Endpoints

### `POST /api/triage/analyze`
Submit a student message for risk analysis and routing.

**Request**
```json
{
  "message": "I feel very anxious about my upcoming exams.",
  "student_id": "anon-session-001",
  "university_id": "default"
}
```

**Response – Low Risk (Academic)**
```json
{
  "risk_level": "LOW",
  "category": "ACADEMIC_STRESS",
  "state": "ACADEMIC_SUPPORT",
  "emergency": false,
  "bypass_llm": false,
  "next_action": "WORKLOAD_AGENT",
  "message": "Your message has been classified for academic support.",
  "disclaimer": "This system provides automated initial triage support only...",
  "confidence": 0.78,
  "resources": [],
  "routing_metadata": {
    "session_id": "uuid-here",
    "module": "Module 3 – Agentic Workload Portal"
  }
}
```

**Response – Critical (Emergency Bypass)**
```json
{
  "risk_level": "CRITICAL",
  "category": "SELF_HARM_CRISIS",
  "state": "EMERGENCY_RESPONSE",
  "emergency": true,
  "bypass_llm": true,
  "next_action": "EMERGENCY_SUPPORT",
  "message": "You deserve immediate support. Please contact emergency services or a trusted person right now.",
  "disclaimer": "This system provides automated initial triage support only...",
  "confidence": 0.97,
  "resources": [
    {
      "id": "emergency_services",
      "name": "Emergency Services",
      "type": "EMERGENCY",
      "phone": "999",
      "available": "24/7",
      "description": "Call immediately if you or someone else is in immediate danger.",
      "verified": true
    },
    {
      "id": "samaritans_uk",
      "name": "Samaritans",
      "type": "CRISIS_LINE",
      "phone": "116 123",
      "available": "24/7",
      "description": "Free confidential listening support, available any time.",
      "verified": true
    }
  ],
  "routing_metadata": {
    "session_id": "uuid-here",
    "llm_invocation_count": 0,
    "bypass_reason": "CRITICAL safety flag — emergency protocol enforced."
  }
}
```

---

### `POST /api/triage/emergency`
Retrieve configured emergency contacts for a university.

**Query param**: `university_id` (optional, defaults to env setting)

**Response**
```json
{
  "university_name": "Default University",
  "global_disclaimer": "...",
  "crisis_message": "You are not alone...",
  "emergency_contacts": [...],
  "online_resources": [...]
}
```

---

### `GET /api/triage/health`
```json
{
  "status": "ok",
  "version": "1.0.0",
  "service": "AI Student Wellbeing Triage Engine – Module 1",
  "disclaimer": "..."
}
```

---

### `GET /api/triage/categories`
Returns the full taxonomy (risk levels, categories, states, next actions).

---

## Architecture – Beginner-Friendly Explanation

### How It Works (Step by Step)

```
Student types a message
        │
        ▼
  [POST /api/triage/analyze]
        │
        ▼
  State Machine: RECEIVED → ANALYZING
        │
        ▼
  ┌─────────────────────────────────────┐
  │   Layer 1: Safety Rules (Always)    │
  │   • 20+ regex patterns              │
  │   • Checks for self-harm language   │
  │   • Checks for indirect crisis cues │
  │   • Checks for negation modifiers   │
  └─────────────────────────────────────┘
        │
        ▼
  CRITICAL? ──YES──► State: CRISIS_DETECTED → EMERGENCY_RESPONSE
                     • Emergency contacts returned immediately
                     • LLM/RAG: NEVER called (count = 0)
                     • Message: "You deserve immediate support."
        │
       NO
        │
        ▼
  ┌─────────────────────────────────────┐
  │   Layer 2: ML Classifier (Support)  │
  │   • TF-IDF + Logistic Regression    │
  │   • Supplements rules, never        │
  │     overrides CRITICAL              │
  └─────────────────────────────────────┘
        │
        ▼
  Category Classifier
  (Academic / Emotional / Financial / Administrative / General)
        │
        ▼
  State Machine: Routes to appropriate support state
        │
        ▼
  Resource Router: Returns next_action code for downstream modules
```

### File-by-File Guide

| File | What It Does |
|------|-------------|
| `app/main.py` | Starts the FastAPI server, registers routes, handles errors |
| `app/config.py` | All settings in one place; reads from `.env` file |
| `app/schemas/triage_schema.py` | Defines the shape of every request and response (Pydantic models) |
| `app/services/risk_detector.py` | The safety brain — detects risk using rules first, then ML |
| `app/services/category_classifier.py` | Decides what kind of problem the student has (academic, financial, etc.) |
| `app/services/emergency_handler.py` | Loads emergency contacts from JSON file (never from an LLM) |
| `app/services/resource_router.py` | Maps category + risk to a routing decision for other modules |
| `app/orchestration/state_machine.py` | Controls the workflow step by step; enforces safety locks |
| `app/api/triage_routes.py` | The FastAPI route handlers that call all the services |
| `app/data/emergency_resources.json` | Admin-configurable emergency contacts (edit before deployment) |

---

## Risk Levels

| Level | Description | LLM Permitted? |
|-------|-------------|----------------|
| `LOW` | General academic / everyday concerns | ✅ Yes |
| `MODERATE` | Noticeable distress; supportive guidance needed | ✅ Yes |
| `HIGH` | Serious distress; human assessment required | ❌ No |
| `CRITICAL` | Explicit self-harm / immediate danger | ❌ No |

---

## Issue Categories

| Category | Examples | Routes To |
|----------|----------|-----------|
| `ACADEMIC_STRESS` | Exams, deadlines, dissertation | Module 3 (Workload Agent) |
| `EMOTIONAL_DISTRESS` | Anxiety, burnout, loneliness | Module 2 (Wellness RAG) |
| `FINANCIAL_PROBLEMS` | Fees, loans, hardship | Module 3 (Financial Aid) |
| `ADMINISTRATIVE_ISSUES` | Extensions, accommodations | Module 3 (Student Portal) |
| `SELF_HARM_CRISIS` | High/Critical risk messages | Human Counsellor |
| `GENERAL_QUERY` | Everything else | Module 2 / Module 3 |

---

## Safety Design Principles

1. **Rules first, always**: Safety regex rules run before any ML. CRITICAL flags cannot be overridden.
2. **Emergency bypass**: Critical messages never reach any generative AI. Zero LLM calls.
3. **Deterministic orchestration**: The state machine uses explicit transition rules. No LLM decides the safety workflow.
4. **Human escalation**: Ambiguous high-risk messages are flagged for human review.
5. **No clinical diagnosis**: The system classifies and routes. It does not diagnose.
6. **Configurable resources**: Emergency contacts come from a JSON file managed by administrators.
7. **No sensitive logging**: Raw message text is redacted in logs by default (`REDACT_MESSAGE_TEXT=true`).
8. **Fail safe**: Any classifier error falls back to rules-only mode.

---

## Integration Guide (For Module 2 & Module 3 Developers)

See `INTEGRATION_CONTRACT.md` for full details.

**Key fields to consume from `/api/triage/analyze`:**

```json
{
  "bypass_llm": false,     // If true: DO NOT invoke any LLM or RAG pipeline
  "emergency": false,      // If true: emergency protocol is active
  "next_action": "...",    // Where to route this message
  "category": "...",       // What kind of problem this is
  "risk_level": "..."      // How serious it is
}
```

**Integration rule**: Always check `bypass_llm` before invoking any AI service. If it is `true`, route to human support only.

---

## Administrator Checklist Before Deployment

- [ ] Replace all `"verified": false` entries in `emergency_resources.json` with real, confirmed contact details
- [ ] Set `UNIVERSITY_ID` in `.env` to match your institution's key in the resources file
- [ ] Set `REDACT_MESSAGE_TEXT=true` in production
- [ ] Review `CORS_ORIGINS` and restrict to your domain(s)
- [ ] Conduct a clinical and legal review with your university's wellbeing and compliance teams
- [ ] Add this system's output to a human oversight workflow (do not run fully autonomously)
- [ ] Test all emergency contacts are reachable before go-live

---

## Important Limitations

- This tool is **not a replacement for professional mental health care**.
- It **cannot guarantee** that all crisis messages will be detected.
- It **does not diagnose** any mental health condition.
- Always maintain a **human-in-the-loop** oversight process.
- Emergency contacts must be **verified by your institution** before deployment.

