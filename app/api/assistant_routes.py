"""
app/api/assistant_routes.py
───────────────────────────
FastAPI routes for the AI Support Assistant and Dual-Store RAG service (Person 2).

Integrates:
  • Pre-LLM Safety Gatekeeper (Person 1) to halt AI during acute crisis.
  • Dual-Store ChromaDB Vector Knowledge Base (Policies + CBT Wellness).
  • Low-confidence similarity fallback check (< 0.60 score) routing to human advisors.
  • Interactive CBT and somatic grounding exercises (/api/assistant/cbt-exercises).
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
    fallback_suggested: bool = Field(False, description="True if query is outside verified knowledge base (< 0.60 score).")
    is_crisis: bool = Field(False, description="True if acute crisis was intercepted.")
    emergency_contacts: List[EmergencyContact] = Field(default_factory=list, description="Emergency contacts if crisis.")
    model_used: Optional[str] = Field(None, description="Model that produced the answer.")
    top_similarity: Optional[float] = Field(None, description="Vector similarity confidence score.")


class CBTExercise(BaseModel):
    id: str = Field(..., description="Unique exercise identifier.")
    name: str = Field(..., description="Clinical exercise title.")
    type: str = Field(..., description="grounding | breathing | cbt_reframing | somatic")
    duration_min: int = Field(..., description="Estimated completion duration in minutes.")
    steps: List[str] = Field(..., description="Sequential clinical action steps.")
    clinical_rationale: str = Field(..., description="Neurobiological and psychological rationale.")
    target_symptoms: List[str] = Field(default_factory=list, description="Specific acute symptoms addressed.")


class CBTExercisesResponse(BaseModel):
    status: str = Field("success", description="Response status.")
    total: int = Field(..., description="Total count of exercises returned.")
    exercises: List[CBTExercise] = Field(default_factory=list, description="List of structured grounding exercises.")


CBT_EXERCISES_DATABASE: List[CBTExercise] = [
    CBTExercise(
        id="grounding_54321",
        name="5-4-3-2-1 Sensory Grounding Guide",
        type="grounding",
        duration_min=5,
        steps=[
            "LOOK: Identify 5 distinct objects you can see right now (e.g., notice their color, shape, or shadow).",
            "TOUCH: Notice 4 physical contact points (e.g., the pressure of your feet against the floor, your back against the chair).",
            "HEAR: Listen carefully and identify 3 distinct sounds around you (e.g., humming AC, outdoor traffic, your own breath).",
            "SMELL: Notice 2 subtle scents around you, or recall two calming scents (e.g., lavender, fresh rain).",
            "TASTE / BREATHE: Notice 1 taste in your mouth, and take one slow, deep breath in and out."
        ],
        clinical_rationale="Activates the prefrontal cortex and sensory neocortex circuits, disrupting limbic hyper-arousal and acute panic spiraling.",
        target_symptoms=["Acute Panic", "Derealization", "Racing Thoughts", "Dissociation"]
    ),
    CBTExercise(
        id="box_breathing",
        name="4-4-4-4 Square Box Breathing",
        type="breathing",
        duration_min=4,
        steps=[
            "STEP 1 (INHALE): Inhale smoothly through your nose for a count of 4 seconds.",
            "STEP 2 (HOLD): Hold your breath gently with relaxed shoulders for a count of 4 seconds.",
            "STEP 3 (EXHALE): Exhale steadily through parted lips for a count of 4 seconds.",
            "STEP 4 (PAUSE): Hold your lungs empty gently for a count of 4 seconds.",
            "CYCLE: Repeat this square sequence for 4 to 6 full cycles."
        ],
        clinical_rationale="Stimulates the vagus nerve and activates parasympathetic dominance, lowering elevated heart rate and cortisol levels.",
        target_symptoms=["Heart Palpitations", "Shortness of Breath", "Hyperventilation", "Pre-Exam Jitters"]
    ),
    CBTExercise(
        id="breathing_478",
        name="4-7-8 Relaxing Breath Timer",
        type="breathing",
        duration_min=5,
        steps=[
            "STEP 1: Place the tip of your tongue against the tissue ridge behind your upper front teeth.",
            "STEP 2: Exhale completely through your mouth, making a gentle whoosh sound.",
            "STEP 3: Close your mouth and inhale quietly through your nose to a mental count of 4.",
            "STEP 4: Hold your breath comfortably for a count of 7 seconds.",
            "STEP 5: Exhale completely through your mouth, making a whoosh sound to a count of 8 seconds.",
            "CYCLE: Repeat the 4-7-8 cycle 4 times."
        ],
        clinical_rationale="Prolonged exhalation relative to inhalation triggers the baroreceptor reflex and induces rapid physiological relaxation.",
        target_symptoms=["Insomnia", "Acute Anxiety Spirals", "Severe Muscle Tightness"]
    ),
    CBTExercise(
        id="progressive_muscle_relaxation",
        name="Progressive Somatic Tension Release",
        type="somatic",
        duration_min=7,
        steps=[
            "STEP 1 (FOREHEAD & JAW): Clench your eyebrows together and tighten your jaw for 5 seconds. Now release and feel the warmth.",
            "STEP 2 (SHOULDERS & NECK): Pull your shoulders up toward your ears, hold tightly for 5 seconds, then drop them completely.",
            "STEP 3 (HANDS & ARMS): Squeeze your fists and tense your forearms for 5 seconds, then release and spread your fingers wide.",
            "STEP 4 (ABDOMEN): Tighten your abdominal muscles for 5 seconds, then breathe out and let your stomach soften completely.",
            "STEP 5 (LEGS & FEET): Curl your toes down and tense your calf muscles for 5 seconds, then let go completely and observe stillness."
        ],
        clinical_rationale="Contrast training between isometric contraction and flaccid release enables conscious relaxation of stress-induced physical tension.",
        target_symptoms=["Jaw Clenching", "Tension Headaches", "Restlessness", "Somatic Tremors"]
    ),
    CBTExercise(
        id="thought_reframing",
        name="Academic Imposter & Panic Reframing",
        type="cbt_reframing",
        duration_min=8,
        steps=[
            "STEP 1 (CATCH THE DISTORTION): Write down the catastrophic belief (e.g., 'If I don't get an A on this assignment, I'm a failure').",
            "STEP 2 (IDENTIFY BIAS): Label the cognitive distortion (e.g., All-or-Nothing Thinking, Catastrophizing, Fortune-Telling).",
            "STEP 3 (EXAMINE EVIDENCE): What concrete factual evidence disproves this thought? What challenges have you navigated before?",
            "STEP 4 (CREATE A BALANCED THOUGHT): Draft a grounded statement: 'One grade does not define my intelligence or future. I can take one 30-minute action step today.'"
        ],
        clinical_rationale="Cognitive restructuring directly alters negative automatic thoughts (NATs), mitigating avoidance behavior and restoring executive function.",
        target_symptoms=["Academic Overwhelm", "Perfectionism", "Procrastination Paralysis", "Imposter Syndrome"]
    )
]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest) -> ChatResponse:
    """
    RAG Assistant Chat Endpoint (Person 2).
    Generates citation-backed answers from campus policy and CBT wellness knowledge stores.
    Protected by Person 1's Pre-LLM Safety Gatekeeper and Person 2's Low-Confidence Fallback Guard (< 0.60 score).
    """
    raw_query = (request.query or request.message or "").strip()
    if not raw_query:
        raise HTTPException(status_code=422, detail="Query or message field must not be empty.")

    logger.info("Assistant chat query received (length=%d)", len(raw_query))

    # ── Step 1: Pre-LLM Safety Screening (Person 1 Gatekeeper) ────────────────
    safety_result = _gatekeeper.evaluate(raw_query, session_id=request.session_id)
    if not safety_result.is_safe or safety_result.bypass_llm:
        logger.warning("Bypassing generative AI for high-risk assistant chat query")
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
            top_similarity=0.0,
        )

    # ── Step 2: RAG Pipeline with ChromaDB & Low-Confidence Guard ─────────────
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
        top_similarity=rag_result.top_similarity,
    )


@router.get("/cbt-exercises", response_model=CBTExercisesResponse)
async def get_cbt_exercises(exercise_type: Optional[str] = None) -> CBTExercisesResponse:
    """
    Returns structured CBT and somatic grounding exercises for student anxiety management (Person 2 Day 3).
    Supports filtering by exercise_type: 'grounding' | 'breathing' | 'cbt_reframing' | 'somatic'.
    """
    if not exercise_type or exercise_type.strip().lower() in ("all", "*"):
        return CBTExercisesResponse(
            status="success",
            total=len(CBT_EXERCISES_DATABASE),
            exercises=CBT_EXERCISES_DATABASE,
        )

    clean_type = exercise_type.strip().lower()
    filtered = [e for e in CBT_EXERCISES_DATABASE if e.type.lower() == clean_type]

    return CBTExercisesResponse(
        status="success",
        total=len(filtered),
        exercises=filtered,
    )
