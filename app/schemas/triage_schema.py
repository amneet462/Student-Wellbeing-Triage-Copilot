"""
app/schemas/triage_schema.py
─────────────────────────────
Pydantic models for all API request/response payloads.

Keeping schemas in one place makes it easy for the other two module developers
to know exactly what this service sends and expects.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


# ── Enumerations ─────────────────────────────────────────────────────────────

class RiskLevel(str, Enum):
    """
    Four-tier risk classification.

    LOW      – General academic / everyday concerns.
    MODERATE – Noticeable distress; supportive guidance recommended.
    HIGH     – Serious distress; prompt human assessment required.
    CRITICAL – Explicit self-harm or immediate danger; emergency bypass activated.
    """
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IssueCategory(str, Enum):
    """
    Supported message categories for routing decisions.
    """
    ACADEMIC_STRESS = "ACADEMIC_STRESS"
    EMOTIONAL_DISTRESS = "EMOTIONAL_DISTRESS"
    FINANCIAL_PROBLEMS = "FINANCIAL_PROBLEMS"
    ADMINISTRATIVE_ISSUES = "ADMINISTRATIVE_ISSUES"
    SELF_HARM_CRISIS = "SELF_HARM_CRISIS"
    GENERAL_QUERY = "GENERAL_QUERY"


class TriageState(str, Enum):
    """
    Deterministic state machine states.
    """
    RECEIVED = "RECEIVED"
    ANALYZING = "ANALYZING"
    CRISIS_DETECTED = "CRISIS_DETECTED"
    EMERGENCY_RESPONSE = "EMERGENCY_RESPONSE"
    NON_CRISIS = "NON_CRISIS"
    ACADEMIC_SUPPORT = "ACADEMIC_SUPPORT"
    EMOTIONAL_SUPPORT = "EMOTIONAL_SUPPORT"
    FINANCIAL_SUPPORT = "FINANCIAL_SUPPORT"
    ADMINISTRATIVE_SUPPORT = "ADMINISTRATIVE_SUPPORT"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class NextAction(str, Enum):
    """
    Destination / next-action codes consumed by the other modules.
    """
    EMERGENCY_SUPPORT = "EMERGENCY_SUPPORT"
    HUMAN_COUNSELLOR = "HUMAN_COUNSELLOR"
    WORKLOAD_AGENT = "WORKLOAD_AGENT"
    WELLNESS_RAG = "WELLNESS_RAG"
    FINANCIAL_AID = "FINANCIAL_AID"
    DISABILITY_SERVICES = "DISABILITY_SERVICES"
    ACADEMIC_SUPPORT = "ACADEMIC_SUPPORT"
    GENERAL_INFO = "GENERAL_INFO"
    HUMAN_REVIEW = "HUMAN_REVIEW"


# ── Request Models ────────────────────────────────────────────────────────────

class StudentMessage(BaseModel):
    """
    Payload for POST /api/triage/analyze.

    Fields
    ------
    message      : The student's raw text input.
    student_id   : Optional anonymised session/student identifier.
                   Do NOT send personally identifiable information here.
    university_id: Selects the correct emergency resource configuration.
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The student's message (max 2000 characters).",
        examples=["I am feeling really anxious about my exams."],
    )
    student_id: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Optional anonymised session identifier. Do NOT include personal details.",
    )
    university_id: Optional[str] = Field(
        default=None,
        max_length=64,
        description="University configuration key (defaults to environment setting).",
    )

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message must not be blank or whitespace-only.")
        return v.strip()


# ── Response Models ───────────────────────────────────────────────────────────

class EmergencyContact(BaseModel):
    """A single verified emergency contact entry."""
    id: str
    name: str
    type: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    text_number: Optional[str] = None
    instruction: Optional[str] = None
    available: Optional[str] = None
    description: str
    verified: bool
    admin_note: Optional[str] = None


class OnlineResource(BaseModel):
    """A single online support resource."""
    id: str
    name: str
    website: str
    description: str
    verified: bool


class TriageResponse(BaseModel):
    """
    Standard response for POST /api/triage/analyze.

    emergency  : True when CRITICAL or HIGH-with-escalation is detected.
    bypass_llm : When True, the calling system MUST NOT forward the message
                 to any generative AI or RAG service.
    """
    risk_level: RiskLevel
    category: IssueCategory
    state: TriageState
    emergency: bool
    bypass_llm: bool
    next_action: NextAction
    message: str
    disclaimer: str
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Classifier confidence (0–1). None when rules alone determine the result.",
    )
    resources: list[EmergencyContact] = Field(
        default_factory=list,
        description="Verified emergency contacts (only populated for critical/emergency responses).",
    )
    routing_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional routing hints for downstream modules.",
    )


class EmergencyResponse(BaseModel):
    """Response for POST /api/triage/emergency."""
    university_name: str
    global_disclaimer: str
    crisis_message: str
    emergency_contacts: list[EmergencyContact]
    online_resources: list[OnlineResource]
    admin_note: str = (
        "Some contacts marked verified=false require administrator confirmation "
        "before this system is deployed in a production environment."
    )


class HealthResponse(BaseModel):
    """Response for GET /api/triage/health."""
    status: str
    version: str
    service: str
    disclaimer: str


class CategoriesResponse(BaseModel):
    """Response for GET /api/triage/categories."""
    risk_levels: dict[str, str]
    categories: dict[str, str]
    states: list[str]
    next_actions: list[str]

