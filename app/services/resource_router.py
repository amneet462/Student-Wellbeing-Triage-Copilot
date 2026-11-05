"""
app/services/resource_router.py
────────────────────────────────
Resource Router – Non-Emergency Routing Decisions.

Maps (category, risk_level) pairs to concrete next-action codes that
Module 2 (RAG / Wellness) and Module 3 (Agentic Workload Portal) consume.

This service ONLY decides WHERE to route. It does not perform routing itself.

Routing Table
─────────────
Category               Risk      Next Action           Downstream Module
─────────────────────────────────────────────────────────────────────────
ACADEMIC_STRESS        LOW       WORKLOAD_AGENT        Module 3
ACADEMIC_STRESS        MODERATE  ACADEMIC_SUPPORT      Module 3
EMOTIONAL_DISTRESS     LOW       WELLNESS_RAG          Module 2
EMOTIONAL_DISTRESS     MODERATE  WELLNESS_RAG          Module 2
EMOTIONAL_DISTRESS     HIGH      HUMAN_COUNSELLOR      Human
FINANCIAL_PROBLEMS     any       FINANCIAL_AID         Module 3
ADMINISTRATIVE_ISSUES  any       DISABILITY_SERVICES   Module 3
                              or ACADEMIC_SUPPORT
SELF_HARM_CRISIS       HIGH      HUMAN_COUNSELLOR      Human
SELF_HARM_CRISIS       CRITICAL  EMERGENCY_SUPPORT     Emergency bypass
GENERAL_QUERY          any       GENERAL_INFO          Module 2 / 3
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.schemas.triage_schema import IssueCategory, NextAction, RiskLevel, TriageState

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """
    Encapsulates the routing decision for a message.

    Fields
    ──────
    next_action     : Where to send the student's request.
    state           : Final triage state after classification.
    bypass_llm      : True means generative AI must NOT be invoked.
    emergency       : True means emergency protocol is active.
    routing_message : User-facing message.
    routing_metadata: Machine-readable hints for downstream services.
    """
    next_action: NextAction
    state: TriageState
    bypass_llm: bool
    emergency: bool
    routing_message: str
    routing_metadata: dict


class ResourceRouter:
    """
    Maps category + risk level to a routing decision.

    This is fully deterministic — no AI/LLM involvement.
    """

    def route(
        self,
        category: IssueCategory,
        risk_level: RiskLevel,
        escalate_to_human: bool = False,
    ) -> RoutingDecision:
        """
        Return the appropriate routing decision.

        Parameters
        ──────────
        category         : Classified issue category.
        risk_level       : Final risk level from RiskDetector.
        escalate_to_human: Escalation flag from RiskAssessment.
        """
        # ── CRITICAL: always emergency bypass ────────────────────────────────
        if risk_level == RiskLevel.CRITICAL:
            return RoutingDecision(
                next_action=NextAction.EMERGENCY_SUPPORT,
                state=TriageState.EMERGENCY_RESPONSE,
                bypass_llm=True,
                emergency=True,
                routing_message=(
                    "You deserve immediate support. "
                    "Please contact emergency services or a trusted person right now. "
                    "Human help is available to you."
                ),
                routing_metadata={
                    "priority": "CRITICAL",
                    "llm_invocation_blocked": True,
                    "reason": "Crisis safety protocol activated.",
                },
            )

        # ── HIGH: human review / counsellor ──────────────────────────────────
        if risk_level == RiskLevel.HIGH or escalate_to_human:
            return RoutingDecision(
                next_action=NextAction.HUMAN_COUNSELLOR,
                state=TriageState.HUMAN_REVIEW,
                bypass_llm=True,
                emergency=False,
                routing_message=(
                    "We can see you are going through a really difficult time. "
                    "A trained counsellor will be in touch to offer you direct support."
                ),
                routing_metadata={
                    "priority": "HIGH",
                    "llm_invocation_blocked": True,
                    "reason": "High distress – routed to human counsellor.",
                },
            )

        # ── MODERATE / LOW by category ────────────────────────────────────────
        return self._route_by_category(category, risk_level)

    def _route_by_category(
        self, category: IssueCategory, risk_level: RiskLevel
    ) -> RoutingDecision:
        """Route non-crisis messages to the appropriate support module."""

        routing_map: dict[IssueCategory, RoutingDecision] = {

            IssueCategory.ACADEMIC_STRESS: RoutingDecision(
                next_action=(
                    NextAction.WORKLOAD_AGENT
                    if risk_level == RiskLevel.LOW
                    else NextAction.ACADEMIC_SUPPORT
                ),
                state=TriageState.ACADEMIC_SUPPORT,
                bypass_llm=False,
                emergency=False,
                routing_message="Your message has been classified for academic support.",
                routing_metadata={
                    "module": "Module 3 – Agentic Workload Portal",
                    "suggested_resource": "Workload Management Agent",
                },
            ),

            IssueCategory.EMOTIONAL_DISTRESS: RoutingDecision(
                next_action=NextAction.WELLNESS_RAG,
                state=TriageState.EMOTIONAL_SUPPORT,
                bypass_llm=False,
                emergency=False,
                routing_message=(
                    "It sounds like you are going through a tough time emotionally. "
                    "Our wellbeing assistant has some resources and guidance for you."
                ),
                routing_metadata={
                    "module": "Module 2 – RAG Wellness Assistant",
                    "suggested_resource": "Mental Wellness RAG",
                },
            ),

            IssueCategory.FINANCIAL_PROBLEMS: RoutingDecision(
                next_action=NextAction.FINANCIAL_AID,
                state=TriageState.FINANCIAL_SUPPORT,
                bypass_llm=False,
                emergency=False,
                routing_message=(
                    "It looks like you need help with a financial matter. "
                    "We will connect you with the Financial Aid team."
                ),
                routing_metadata={
                    "module": "Module 3 – Student Portal",
                    "suggested_resource": "Financial Aid Office",
                },
            ),

            IssueCategory.ADMINISTRATIVE_ISSUES: RoutingDecision(
                next_action=NextAction.ACADEMIC_SUPPORT,
                state=TriageState.ADMINISTRATIVE_SUPPORT,
                bypass_llm=False,
                emergency=False,
                routing_message=(
                    "We will route your administrative query to the appropriate support team."
                ),
                routing_metadata={
                    "module": "Module 3 – Student Portal",
                    "suggested_resource": "Student Services / Disability Services",
                },
            ),

            IssueCategory.SELF_HARM_CRISIS: RoutingDecision(
                next_action=NextAction.HUMAN_COUNSELLOR,
                state=TriageState.HUMAN_REVIEW,
                bypass_llm=True,
                emergency=False,
                routing_message=(
                    "We care about your wellbeing. A trained counsellor is being notified "
                    "and will reach out to offer you support."
                ),
                routing_metadata={
                    "priority": "HIGH",
                    "llm_invocation_blocked": True,
                    "reason": "Self-harm category – routed to human counsellor.",
                },
            ),

            IssueCategory.GENERAL_QUERY: RoutingDecision(
                next_action=NextAction.GENERAL_INFO,
                state=TriageState.NON_CRISIS,
                bypass_llm=False,
                emergency=False,
                routing_message="Your query has been received. We will help you find the right information.",
                routing_metadata={
                    "module": "Module 2 or Module 3",
                    "suggested_resource": "General Student Services",
                },
            ),
        }

        decision = routing_map.get(category)
        if decision is None:
            logger.warning("Unknown category '%s', falling back to GENERAL_INFO.", category)
            decision = routing_map[IssueCategory.GENERAL_QUERY]

        logger.info(
            "Routing decision | category=%s | risk=%s | next_action=%s | bypass_llm=%s",
            category.value,
            risk_level.value,
            decision.next_action.value,
            decision.bypass_llm,
        )
        return decision

