"""
app/api/assistant_routes.py
───────────────────────────
FastAPI routes for the AI Support Assistant and Dual-Store RAG service.
Initially stubbed with verified mock responses for team development.
"""

from __future__ import annotations

import logging
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["Assistant & RAG"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class Citation(BaseModel):
    document: str = Field(..., description="Name of the official university policy or clinical source document.")
    section: str = Field(..., description="Specific section, clause, or chapter.")
    page: Optional[int] = Field(None, description="Page number if available.")
    excerpt: Optional[str] = Field(None, description="Verbatim citation snippet.")


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Client session ID for state continuity.")
    query: str = Field(..., min_length=1, max_length=2000, description="Student's inquiry.")
    category: Optional[str] = Field(None, description="Classified category from triage engine.")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Assistant response text with verified information.")
    citations: List[Citation] = Field(default_factory=list, description="Verified citations backing the answer.")
    safety_checked: bool = Field(True, description="Indicates safety pre-screening passed.")
    fallback_suggested: bool = Field(False, description="True if query is outside verified knowledge base.")


class CBTExercise(BaseModel):
    id: str
    name: str
    type: str
    duration_min: int
    steps: List[str]
    clinical_rationale: str


class CBTExercisesResponse(BaseModel):
    status: str
    exercises: List[CBTExercise]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest) -> ChatResponse:
    """
    RAG Assistant Chat Endpoint (Person 2).
    Generates citation-backed answers from campus policy and CBT wellness knowledge stores.
    """
    logger.info("Assistant chat query received: %s (session: %s)", request.query[:50], request.session_id)
    
    # Mock intelligent response for team development
    query_lower = request.query.lower()
    
    if "extension" in query_lower or "deadline" in query_lower or "mitigating" in query_lower:
        return ChatResponse(
            reply=(
                "Under university academic regulations, you are entitled to request a formal coursework "
                "extension if you encounter unforeseen personal or medical difficulties. Extension requests "
                "should typically be submitted at least 48 hours prior to the assessment deadline through "
                "the student portal with relevant supporting documentation."
            ),
            citations=[
                Citation(
                    document="University Academic Regulations Handbook 2026",
                    section="Section 4.3 (Extenuating Circumstances & Coursework Deadlines)",
                    page=19,
                    excerpt="Applications for deadline extensions under extenuating circumstances must be registered 48h prior to submission."
                )
            ],
            safety_checked=True,
            fallback_suggested=False
        )
    
    if "panic" in query_lower or "anxious" in query_lower or "breathe" in query_lower or "grounding" in query_lower:
        return ChatResponse(
            reply=(
                "When experiencing acute exam anxiety or panic, cognitive psychology recommends the 5-4-3-2-1 "
                "grounding technique to regulate your nervous system. Try identifying 5 things you can see, "
                "4 things you can physically touch, 3 things you can hear, 2 things you can smell, and 1 slow breath."
            ),
            citations=[
                Citation(
                    document="Clinical Psychoeducation & Anxiety Management Guide",
                    section="Module 2 (Acute Somatic Grounding)",
                    page=7,
                    excerpt="Sensory grounding interrupts amygdala-driven panic loops by re-anchoring cognitive attention."
                )
            ],
            safety_checked=True,
            fallback_suggested=False
        )

    # General campus guidance fallback
    return ChatResponse(
        reply=(
            "I have retrieved your university's student guidance. For general coursework advice, syllabus "
            "breakdown, or campus support services, please check the Workload Planner tab or visit the "
            "Campus Support Directory to connect directly with your academic advisor."
        ),
        citations=[
            Citation(
                document="Student Wellbeing & Academic Support Charter 2026",
                section="Section 1.1 (Student Guidance & Support Directory)",
                page=3
            )
        ],
        safety_checked=True,
        fallback_suggested=False
    )


@router.get("/cbt-exercises", response_model=CBTExercisesResponse)
async def get_cbt_exercises(exercise_type: Optional[str] = None) -> CBTExercisesResponse:
    """
    Returns structured CBT and somatic grounding exercises for student anxiety management.
    """
    all_exercises = [
        CBTExercise(
            id="grounding_54321",
            name="5-4-3-2-1 Sensory Grounding",
            type="grounding",
            duration_min=5,
            steps=[
                "Look around you and name 5 things you can see.",
                "Notice 4 physical sensations you can touch (e.g. your feet on the floor, your chair).",
                "Focus on 3 distinct sounds you can hear in your environment.",
                "Notice 2 things you can smell (or two scents you enjoy).",
                "Notice 1 thing you can taste, or take one slow, deliberate breath."
            ],
            clinical_rationale="Engages sensory neocortex circuits to rapidly break acute cognitive panic spiraling."
        ),
        CBTExercise(
            id="box_breathing",
            name="4-4-4-4 Box Breathing",
            type="breathing",
            duration_min=4,
            steps=[
                "Inhale slowly through your nose for a count of 4.",
                "Hold your breath gently for a count of 4.",
                "Exhale smoothly through your mouth for a count of 4.",
                "Hold empty lungs gently for a count of 4.",
                "Repeat this square cycle 4 times."
            ],
            clinical_rationale="Stimulates the vagus nerve, initiating parasympathetic heart-rate deceleration."
        ),
        CBTExercise(
            id="thought_reframing",
            name="Academic Imposter Reframing",
            type="cbt_reframing",
            duration_min=8,
            steps=[
                "Identify the catastrophic thought (e.g. 'If I fail this exam, my entire future is over').",
                "Identify the cognitive distortion (All-or-Nothing thinking / Catastrophizing).",
                "Evaluate the factual evidence: What have you achieved in the past?",
                "Draft a rational alternative thought: 'One exam does not define my capability; I can take concrete study steps today.'"
            ],
            clinical_rationale="Cognitive reappraisal reduces cortisol response and restores executive planning function."
        )
    ]
    
    if exercise_type:
        filtered = [e for e in all_exercises if e.type.lower() == exercise_type.lower()]
        return CBTExercisesResponse(status="success", exercises=filtered)
        
    return CBTExercisesResponse(status="success", exercises=all_exercises)

