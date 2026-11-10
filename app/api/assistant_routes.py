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


class CBTPhase(BaseModel):
    phase_name: str
    duration_seconds: int
    instruction: str


class BreathingProtocolResponse(BaseModel):
    id: str
    name: str
    total_cycles: int
    cycle_duration_seconds: int
    phases: List[CBTPhase]
    clinical_rationale: str
    precautions: str


class GroundingStep(BaseModel):
    sense: str
    count: int
    prompt: str
    guidance: str


class GroundingProtocolResponse(BaseModel):
    id: str
    name: str
    steps: List[GroundingStep]
    clinical_rationale: str
    recommended_duration_min: int


class MuscleGroupStep(BaseModel):
    muscle_group: str
    tension_seconds: int
    release_seconds: int
    instruction: str


class PMRProtocolResponse(BaseModel):
    id: str
    name: str
    total_steps: int
    steps: List[MuscleGroupStep]
    clinical_rationale: str


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


@router.get("/cbt/478-breathing", response_model=BreathingProtocolResponse)
async def get_478_breathing_protocol() -> BreathingProtocolResponse:
    """
    Returns interactive 4-7-8 parasympathetic calming breathing protocol.
    4s Inhale, 7s Hold, 8s Exhale with neurobiological rationale.
    """
    return BreathingProtocolResponse(
        id="breathing_478",
        name="4-7-8 Relaxing Vagal Breathing Protocol",
        total_cycles=4,
        cycle_duration_seconds=19,
        phases=[
            CBTPhase(phase_name="Inhale", duration_seconds=4, instruction="Breathe in quietly through your nose into your diaphragm for 4 seconds."),
            CBTPhase(phase_name="Hold", duration_seconds=7, instruction="Hold your breath gently without straining your throat or chest for 7 seconds."),
            CBTPhase(phase_name="Exhale", duration_seconds=8, instruction="Exhale completely through your mouth with a soft 'whoosh' sound for 8 seconds."),
        ],
        clinical_rationale=(
            "Developed by Dr. Andrew Weil. The prolonged 8-second exhale stimulates the vagus nerve, "
            "triggering acetylcholine release which actively decelerates cardiac rhythm and silences sympathetic fight-or-flight arousal."
        ),
        precautions="Do not practice while driving or operating equipment. If you feel lightheaded, return to normal tidal breathing."
    )


@router.get("/cbt/54321-grounding", response_model=GroundingProtocolResponse)
async def get_54321_grounding_protocol() -> GroundingProtocolResponse:
    """
    Returns interactive 5-4-3-2-1 somatic sensory grounding sequence for panic desensitization.
    """
    return GroundingProtocolResponse(
        id="grounding_54321",
        name="5-4-3-2-1 Somatosensory De-escalation Protocol",
        recommended_duration_min=5,
        steps=[
            GroundingStep(
                sense="Sight (Visual)",
                count=5,
                prompt="Acknowledge 5 things you see around you right now.",
                guidance="Look for small details: the texture of a desk, light reflection on a wall, a pen, a plant, a shadow."
            ),
            GroundingStep(
                sense="Touch (Tactile)",
                count=4,
                prompt="Acknowledge 4 physical sensations you can feel.",
                guidance="Notice the firm pressure of your feet against the floor, the fabric of your sleeves, the chair supporting your back, or the cool air on your hands."
            ),
            GroundingStep(
                sense="Hearing (Auditory)",
                count=3,
                prompt="Acknowledge 3 distinct sounds you can hear.",
                guidance="Listen past the room: distant traffic, the hum of computer ventilation, a clock ticking, or your own breath."
            ),
            GroundingStep(
                sense="Smell (Olfactory)",
                count=2,
                prompt="Acknowledge 2 scents you can detect.",
                guidance="Notice your coffee, room scent, paper, or visualize two calming scents you love (lavender, ocean pine)."
            ),
            GroundingStep(
                sense="Taste / Breath (Gustatory)",
                count=1,
                prompt="Acknowledge 1 taste, or take one deep grounding diaphragmatic breath.",
                guidance="Notice the lingering taste of mint or water, release your tongue from the roof of your mouth, and drop your shoulders."
            ),
        ],
        clinical_rationale=(
            "Forces cognitive attention away from catastrophic internal rumination loops in the amygdala "
            "into the parietal and occipital sensory cortices, grounding the nervous system in immediate present-moment reality."
        )
    )


@router.get("/cbt/box-breathing", response_model=BreathingProtocolResponse)
async def get_box_breathing_protocol() -> BreathingProtocolResponse:
    """
    Returns 4-4-4-4 Tactical Box Breathing protocol for acute exam stress regulation.
    """
    return BreathingProtocolResponse(
        id="box_breathing",
        name="4-4-4-4 Tactical Box Breathing",
        total_cycles=4,
        cycle_duration_seconds=16,
        phases=[
            CBTPhase(phase_name="Inhale", duration_seconds=4, instruction="Inhale smoothly through your nose for 4 counts, expanding lower belly."),
            CBTPhase(phase_name="Hold (Full)", duration_seconds=4, instruction="Hold air softly in your lungs for 4 counts with relaxed shoulders."),
            CBTPhase(phase_name="Exhale", duration_seconds=4, instruction="Exhale smoothly through your mouth for 4 counts, emptying lungs evenly."),
            CBTPhase(phase_name="Hold (Empty)", duration_seconds=4, instruction="Pause with empty lungs for 4 counts before the next inhalation cycle."),
        ],
        clinical_rationale=(
            "Used by tactical first responders and clinical psychologists to re-balance blood CO2 and O2 concentrations, "
            "stabilizing autonomic nervous system fluctuation during acute cognitive performance stress."
        ),
        precautions="Maintain smooth, steady pacing rather than forceful gasping."
    )


@router.get("/cbt/progressive-muscle-relaxation", response_model=PMRProtocolResponse)
async def get_pmr_protocol() -> PMRProtocolResponse:
    """
    Returns Progressive Muscle Relaxation (PMR) protocol.
    """
    return PMRProtocolResponse(
        id="pmr_protocol",
        name="Jacobsonian Progressive Muscle Relaxation (PMR)",
        total_steps=5,
        steps=[
            MuscleGroupStep(muscle_group="Hands and Forearms", tension_seconds=5, release_seconds=10, instruction="Clench both hands into tight fists. Feel tension in wrists and forearms. Release suddenly and let fingers unclench completely."),
            MuscleGroupStep(muscle_group="Shoulders and Trapezius", tension_seconds=5, release_seconds=10, instruction="Shrug your shoulders up toward your ears, creating deliberate tension. Drop them abruptly and feel warmth flooding your neck."),
            MuscleGroupStep(muscle_group="Facial Muscles and Jaw", tension_seconds=5, release_seconds=10, instruction="Scrunch your forehead, squeeze eyes shut, and gently clench your jaw. Release completely, letting jaw drop slightly open."),
            MuscleGroupStep(muscle_group="Abdomen and Core", tension_seconds=5, release_seconds=10, instruction="Tighten your stomach muscles as if preparing for impact. Release and let your belly soften completely."),
            MuscleGroupStep(muscle_group="Feet and Calves", tension_seconds=5, release_seconds=10, instruction="Point your toes upward toward your shins, tensing calves. Release and let feet fall outward in complete relaxation."),
        ],
        clinical_rationale="Contrasting deliberate muscular isometric tension with sudden autonomic release teaches the brain somatic discrimination of chronic stress tension."
    )

