# Integration Contract — Module 1: AI Safety & Risk Triage Engine

**Version**: 1.0.0  
**Author**: Module 1 Team  
**Purpose**: Defines the API contract for Module 2 (RAG/Wellness) and Module 3 (Agentic Workload Portal) to integrate with this service.

---

## Base URL

```
http://<host>:8000/api/triage
```

---

## Critical Integration Rule

> **If `bypass_llm` is `true` in any response, the calling module MUST NOT invoke any generative AI, LLM, or RAG pipeline. Route to human support only.**

---

## Endpoints

### 1. `POST /api/triage/analyze`

Analyzes a student message.

**Request**
```json
{
  "message": "string (1–2000 chars, required)",
  "student_id": "string (optional, max 64 chars, anonymised only)",
  "university_id": "string (optional, matches emergency_resources.json key)"
}
```

**Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `risk_level` | `RiskLevel` | `LOW` \| `MODERATE` \| `HIGH` \| `CRITICAL` |
| `category` | `IssueCategory` | See categories below |
| `state` | `TriageState` | Current state machine state |
| `emergency` | `bool` | True when CRITICAL or escalated |
| `bypass_llm` | `bool` | **True = do NOT call any AI service** |
| `next_action` | `NextAction` | Where to route this request |
| `message` | `string` | User-facing triage message |
| `disclaimer` | `string` | Clinical disclaimer (always present) |
| `confidence` | `float \| null` | ML classifier confidence (0–1) |
| `resources` | `EmergencyContact[]` | Populated only for CRITICAL responses |
| `routing_metadata` | `object` | Integration hints for downstream services |

---

### 2. `POST /api/triage/emergency`

Returns emergency contacts for a university.

**Query param**: `university_id` (optional string)

**Response**: `EmergencyResponse` object (see schemas).

---

### 3. `GET /api/triage/health`

Returns service health status.

---

### 4. `GET /api/triage/categories`

Returns the full taxonomy of risk levels, categories, states, and next actions.

---

## Enumerations

### `RiskLevel`

| Value | Meaning | LLM Allowed? |
|-------|---------|--------------|
| `LOW` | General / everyday concern | ✅ |
| `MODERATE` | Noticeable distress | ✅ |
| `HIGH` | Serious distress | ❌ |
| `CRITICAL` | Self-harm / immediate danger | ❌ |

### `IssueCategory`

| Value | Description |
|-------|-------------|
| `ACADEMIC_STRESS` | Coursework, exams, grades |
| `EMOTIONAL_DISTRESS` | Anxiety, depression, burnout |
| `FINANCIAL_PROBLEMS` | Fees, loans, hardship |
| `ADMINISTRATIVE_ISSUES` | Extensions, accommodations, enrolment |
| `SELF_HARM_CRISIS` | High/Critical risk — routed to human |
| `GENERAL_QUERY` | General questions |

### `TriageState`

| Value | Description |
|-------|-------------|
| `RECEIVED` | Message received |
| `ANALYZING` | Analysis in progress |
| `CRISIS_DETECTED` | CRITICAL risk flagged (transitions to EMERGENCY_RESPONSE) |
| `EMERGENCY_RESPONSE` | Emergency protocol active — no LLM |
| `HUMAN_REVIEW` | Ambiguous or HIGH risk — human must review |
| `NON_CRISIS` | General, non-crisis message |
| `ACADEMIC_SUPPORT` | Academic routing |
| `EMOTIONAL_SUPPORT` | Emotional / wellness routing |
| `FINANCIAL_SUPPORT` | Financial routing |
| `ADMINISTRATIVE_SUPPORT` | Administrative routing |

### `NextAction`

| Value | Consuming Module |
|-------|-----------------|
| `EMERGENCY_SUPPORT` | Emergency services (not AI) |
| `HUMAN_COUNSELLOR` | University counselling team |
| `WORKLOAD_AGENT` | **Module 3** — Agentic Workload Manager |
| `WELLNESS_RAG` | **Module 2** — RAG Wellness Assistant |
| `FINANCIAL_AID` | **Module 3** — Financial Aid |
| `DISABILITY_SERVICES` | **Module 3** — Disability / Admin |
| `ACADEMIC_SUPPORT` | **Module 3** — Academic Support |
| `GENERAL_INFO` | **Module 2 or 3** — General info |
| `HUMAN_REVIEW` | Human counsellor review queue |

---

## State Transition Rules

```
RECEIVED → ANALYZING → CRISIS_DETECTED → EMERGENCY_RESPONSE (locked, no LLM)
                     → HUMAN_REVIEW                          (locked, no LLM)
                     → ACADEMIC_SUPPORT                      (Module 3)
                     → EMOTIONAL_SUPPORT                     (Module 2)
                     → FINANCIAL_SUPPORT                     (Module 3)
                     → ADMINISTRATIVE_SUPPORT                (Module 3)
                     → NON_CRISIS                            (Module 2 or 3)
```

**Invariants**:
- `CRISIS_DETECTED` **always** transitions to `EMERGENCY_RESPONSE`
- `EMERGENCY_RESPONSE` and `HUMAN_REVIEW` **never** transition to AI workflow states
- `bypass_llm=true` means no AI invocation under any circumstances

---

## Routing Decision Table

| category | risk_level | bypass_llm | next_action | module |
|----------|-----------|------------|-------------|--------|
| `ACADEMIC_STRESS` | LOW | false | `WORKLOAD_AGENT` | Module 3 |
| `ACADEMIC_STRESS` | MODERATE | false | `ACADEMIC_SUPPORT` | Module 3 |
| `EMOTIONAL_DISTRESS` | LOW/MODERATE | false | `WELLNESS_RAG` | Module 2 |
| `EMOTIONAL_DISTRESS` | HIGH | true | `HUMAN_COUNSELLOR` | Human |
| `FINANCIAL_PROBLEMS` | any | false | `FINANCIAL_AID` | Module 3 |
| `ADMINISTRATIVE_ISSUES` | any | false | `ACADEMIC_SUPPORT` | Module 3 |
| `GENERAL_QUERY` | LOW | false | `GENERAL_INFO` | Module 2/3 |
| `SELF_HARM_CRISIS` | HIGH | true | `HUMAN_COUNSELLOR` | Human |
| `SELF_HARM_CRISIS` | CRITICAL | true | `EMERGENCY_SUPPORT` | Emergency |
| any | CRITICAL | **true** | `EMERGENCY_SUPPORT` | Emergency |

---

## Example Integration Code (Python)

```python
import httpx

TRIAGE_URL = "http://localhost:8000/api/triage/analyze"

def handle_student_message(message: str, student_id: str | None = None):
    response = httpx.post(TRIAGE_URL, json={
        "message": message,
        "student_id": student_id,
    })
    triage = response.json()

    # SAFETY CHECK — always do this first
    if triage["bypass_llm"]:
        # Do NOT call any LLM or RAG
        return handle_human_or_emergency(triage)

    # Route based on next_action
    next_action = triage["next_action"]
    if next_action == "WORKLOAD_AGENT":
        return call_module_3_workload_agent(message, triage)
    elif next_action == "WELLNESS_RAG":
        return call_module_2_rag(message, triage)
    elif next_action == "FINANCIAL_AID":
        return call_module_3_financial(message, triage)
    # ... etc.
```

---

## Error Responses

| HTTP Code | Meaning |
|-----------|---------|
| `200` | Success |
| `422` | Validation error (empty message, field too long, etc.) |
| `500` | Internal server error |

All `422` responses follow FastAPI's standard validation error format.  
All `500` responses include the clinical disclaimer in the body.

