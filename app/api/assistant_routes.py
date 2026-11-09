"""
app/api/assistant_routes.py
───────────────────────────
FastAPI routes for the AI Support Assistant and Dual-Store RAG service (Person 2).

Integrates:
  • Pre-LLM Safety Gatekeeper (Person 1) to halt AI during acute crisis.
  • Dual-Store ChromaDB Vector Knowledge Base (Policies + CBT Wellness).
  • Google Gemini Free-Tier RAG Engine with prompt-enforced verbatim citations.
  • Deterministic local fallback ensuring 0 cost and token minimization.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.schemas.triage_schema import EmergencyContact
from app.services.safety_gatekeeper import SafetyGatekeeper
from app.services.rag.gemini_rag import GeminiRAGAssistant, RAGAnswer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["Assistant & RAG"])

# Singleton service instances
_gatekeeper = SafetyGatekeeper()
_rag_assistant = GeminiRAGAssistant()


# ── Schemas ───────────────────────────────────────────────────────────────────

class Citation(BaseModel):
    document: str = Field(..., description="Name of official university policy or clinical guide.")
    section: str = Field(..., description="Specific section, clause, or chapter.")
    page: Optional[int] = Field(None, description="Page number or chunk index.")
    excerpt: Optional[str] = Field(None, description="Verbatim citation snippet.")


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Client session ID for state continuity.")
    query: Optional[str] = Field(None, description="Student's inquiry (alias: message).")
    message: Optional[str] = Field(None, description="Alternative field for student's inquiry.")
    category: Optional[str] = Field(None, description="Classified category from triage engine.")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Assistant response text with verified information.")
    citations: List[Citation] = Field(default_factory=list, description="Verified citations backing the answer.")
    safety_checked: bool = Field(True, description="Indicates safety pre-screening passed.")
    fallback_suggested: bool = Field(False, description="True if query is outside verified knowledge base.")
    is_crisis: bool = Field(False, description="True if acute crisis was intercepted.")
    emergency_contacts: List[EmergencyContact] = Field(default_factory=list, description="Emergency contacts if crisis.")
    model_used: Optional[str] = Field(None, description="Model that produced the answer.")


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
    Protected by Person 1's Pre-LLM Safety Gatekeeper.
    """
    raw_query = (request.query or request.message or "").strip()
    if not raw_query:
        raise HTTPException(status_code=422, detail="Query or message field must not be empty.")

    logger.info("Assistant chat query received: '%s' (session: %s)", raw_query[:60], request.session_id)

    # ── Step 1: Pre-LLM Safety Screening (Person 1 Gatekeeper) ────────────────
    safety_result = _gatekeeper.evaluate(raw_query, session_id=request.session_id)
    if not safety_result.is_safe or safety_result.bypass_llm:
        logger.warning("Bypassing generative AI for high-risk chat query: '%s'", raw_query[:40])
        return ChatResponse(
            reply=safety_result.crisis_message or "Emergency protocol active.",
            citations=[
                Citation(
                    document="Clinical Emergency Safety Protocol 2026",
                    section="Section 1.0 (Zero-LLM Immediate Bypass)",
                    page=1,
                    excerpt="Generative AI is halted when self-harm or acute crisis indicators are detected."
                )
            ],
            safety_checked=True,
            fallback_suggested=False,
            is_crisis=True,
            emergency_contacts=safety_result.emergency_contacts,
            model_used="safety-gatekeeper-bypass",
        )

    # ── Step 2: RAG Pipeline with ChromaDB & Gemini ───────────────────────────
    rag_result: RAGAnswer = _rag_assistant.generate_response(raw_query, category=request.category)

    # Map citations to response schema
    out_citations = [
        Citation(
            document=c.document,
            section=c.section,
            page=c.page,
            excerpt=c.excerpt,
        )
        for c in rag_result.citations
    ]

    return ChatResponse(
        reply=rag_result.reply,
        citations=out_citations,
        safety_checked=True,
        fallback_suggested=rag_result.fallback_suggested,
        is_crisis=False,
        emergency_contacts=[],
        model_used=rag_result.model_used,
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
