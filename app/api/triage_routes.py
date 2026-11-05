"""
app/api/triage_routes.py
─────────────────────────
FastAPI route definitions for the Triage Engine.

Endpoints
─────────
  POST /api/triage/analyze     – Submit a student message for triage.
  POST /api/triage/emergency   – Retrieve configured emergency resources.
  GET  /api/triage/health      – Service health check.
  GET  /api/triage/categories  – List supported categories and risk levels.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import APP_VERSION, CLINICAL_DISCLAIMER
from app.orchestration.state_machine import TriageStateMachine
from app.schemas.triage_schema import (
    CategoriesResponse,
    EmergencyResponse,
    HealthResponse,
    IssueCategory,
    NextAction,
    RiskLevel,
    StudentMessage,
    TriageResponse,
    TriageState,
)
from app.services.category_classifier import CategoryClassifier
from app.services.emergency_handler import EmergencyHandler
from app.services.resource_router import ResourceRouter
from app.services.risk_detector import RiskDetector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/triage", tags=["Triage"])

# ── Singleton service instances (created once at import time) ─────────────────
_risk_detector = RiskDetector()
_category_classifier = CategoryClassifier()
_resource_router = ResourceRouter()
_emergency_handler = EmergencyHandler()
_state_machine = TriageStateMachine()


# ── POST /api/triage/analyze ──────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=TriageResponse,
    summary="Analyze a student message for risk and category",
    description=(
        "Accepts a student's message and returns a risk level, category, "
        "routing decision, and — when critical — emergency contacts. "
        "This endpoint enforces the emergency bypass: "
        "critical messages are NEVER forwarded to any generative AI service."
    ),
)
async def analyze_message(payload: StudentMessage) -> TriageResponse:
    """
    Full triage pipeline:

    1. Create a state-machine session.
    2. Run deterministic risk detection (Layer 1 rules, then Layer 2 ML).
    3. Classify into an issue category.
    4. Advance the state machine.
    5. If CRITICAL → emergency bypass, return pre-configured contacts.
    6. Otherwise → route to the appropriate downstream module.
    """
    session = _state_machine.create_session()
    logger.info("[session=%s] /analyze request received.", session.session_id)

    # ── Step 1: Risk Detection ────────────────────────────────────────────────
    assessment = _risk_detector.assess(payload.message)
    final_risk = assessment.final_risk_level

    # ── Step 2: Category Classification ──────────────────────────────────────
    cat_result = _category_classifier.classify(payload.message, risk_level=final_risk)
    category = cat_result.category

    # ── Step 3: State Machine Transition ──────────────────────────────────────
    category_flag = _state_machine.category_to_flag(category.value)
    final_state = _state_machine.transition(
        session,
        risk_level=final_risk,
        category_flag=category_flag,
        trigger_label=f"risk={final_risk.value}|category={category.value}",
    )

    # ── Step 4: Emergency Bypass ──────────────────────────────────────────────
    # This is the HARD SAFETY GATE.
    # If CRITICAL: return emergency response immediately. No LLM. No RAG. Full stop.
    if final_risk == RiskLevel.CRITICAL:
        logger.warning(
            "[session=%s] CRITICAL risk detected. Emergency bypass activated. "
            "LLM invocation count: 0.",
            session.session_id,
        )
        resources = _emergency_handler.get_critical_contacts_only(
            payload.university_id
        )
        return TriageResponse(
            risk_level=RiskLevel.CRITICAL,
            category=IssueCategory.SELF_HARM_CRISIS,
            state=TriageState.EMERGENCY_RESPONSE,
            emergency=True,
            bypass_llm=True,
            next_action=NextAction.EMERGENCY_SUPPORT,
            message=(
                "You deserve immediate support. "
                "Please contact emergency services or a trusted person right now. "
                "Human help is here for you — you do not have to face this alone."
            ),
            disclaimer=CLINICAL_DISCLAIMER,
            confidence=assessment.ml_confidence,
            resources=resources,
            routing_metadata={
                "session_id": session.session_id,
                "llm_invocation_count": 0,
                "bypass_reason": "CRITICAL safety flag — emergency protocol enforced.",
                "triggered_rules": assessment.triggered_rules,
                "state_history": [t.to_state.value for t in session.history],
            },
        )

    # ── Step 5: Non-Crisis Routing ────────────────────────────────────────────
    routing = _resource_router.route(
        category=category,
        risk_level=final_risk,
        escalate_to_human=assessment.escalate_to_human,
    )

    return TriageResponse(
        risk_level=final_risk,
        category=category,
        state=final_state,
        emergency=routing.emergency,
        bypass_llm=routing.bypass_llm,
        next_action=routing.next_action,
        message=routing.routing_message,
        disclaimer=CLINICAL_DISCLAIMER,
        confidence=assessment.ml_confidence,
        resources=[],
        routing_metadata={
            "session_id": session.session_id,
            "llm_invocation_count": 0 if routing.bypass_llm else None,
            "category_confidence": cat_result.confidence,
            "category_method": cat_result.method,
            "escalated": assessment.escalate_to_human,
            "notes": assessment.notes,
            **routing.routing_metadata,
        },
    )


# ── POST /api/triage/emergency ────────────────────────────────────────────────

@router.post(
    "/emergency",
    response_model=EmergencyResponse,
    summary="Retrieve configured emergency support contacts",
    description=(
        "Returns the administrator-configured emergency contacts and resources "
        "for the specified university. "
        "These contacts are NEVER generated by an AI — only configured values are returned."
    ),
)
async def get_emergency_resources(university_id: str | None = None) -> EmergencyResponse:
    """Return verified emergency resources. No LLM involved."""
    logger.info("Emergency resources requested | university_id=%s", university_id)
    return _emergency_handler.get_emergency_response(university_id)


# ── GET /api/triage/health ────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Triage service health check",
)
async def health_check() -> HealthResponse:
    """Returns the operational status of the triage service."""
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        service="AI Student Wellbeing Triage Engine – Module 1",
        disclaimer=CLINICAL_DISCLAIMER,
    )


# ── GET /api/triage/categories ────────────────────────────────────────────────

@router.get(
    "/categories",
    response_model=CategoriesResponse,
    summary="List supported risk levels, categories, and routing actions",
)
async def get_categories() -> CategoriesResponse:
    """Returns the full taxonomy used by the triage engine for integration reference."""
    return CategoriesResponse(
        risk_levels={
            "LOW": "General academic or everyday concerns.",
            "MODERATE": "Noticeable emotional distress; supportive guidance recommended.",
            "HIGH": "Serious distress; prompt human assessment required.",
            "CRITICAL": "Explicit self-harm or immediate danger; emergency bypass activated.",
        },
        categories={
            "ACADEMIC_STRESS": "Coursework, exams, grades, deadlines, dissertation.",
            "EMOTIONAL_DISTRESS": "Anxiety, depression, loneliness, burnout.",
            "FINANCIAL_PROBLEMS": "Fees, loans, financial hardship.",
            "ADMINISTRATIVE_ISSUES": "Extensions, accommodations, enrolment.",
            "SELF_HARM_CRISIS": "Self-harm or crisis indicators (HIGH/CRITICAL).",
            "GENERAL_QUERY": "General questions not matching other categories.",
        },
        states=[s.value for s in TriageState],
        next_actions=[a.value for a in NextAction],
    )

