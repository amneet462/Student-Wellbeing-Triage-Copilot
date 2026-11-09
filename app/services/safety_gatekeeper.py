"""
app/services/safety_gatekeeper.py
─────────────────────────────────
Pre-LLM Safety Gatekeeper Engine (Person 1).

Responsibilities:
  1. Intercept all incoming chat queries BEFORE they reach any LLM or RAG pipeline.
  2. Evaluate deterministic regex rules and statistical risk scores.
  3. If HIGH or CRITICAL risk is detected:
       - Immediately HALT downstream processing (zero generative AI invocation).
       - Record an immutable, redacted audit log entry.
       - Return verified campus emergency telephone numbers.
  4. If LOW or MODERATE:
       - Allow query to safely proceed to the RAG Assistant.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.schemas.triage_schema import EmergencyContact, RiskLevel
from app.services.audit_logger import CrisisAuditLogger
from app.services.emergency_handler import EmergencyHandler
from app.services.risk_detector import RiskDetector

logger = logging.getLogger(__name__)

CRISIS_MESSAGE = (
    "⚠️ CLINICAL SAFETY PROTOCOL ACTIVE: Acute distress or self-harm indicators detected. "
    "Automated generative AI assistance is immediately stopped to safeguard your wellbeing. "
    "Please connect immediately with trained professional human support via the 24/7 contacts below."
)


@dataclass
class GatekeeperResult:
    """Result of the pre-LLM safety screening."""
    is_safe: bool
    risk_level: RiskLevel
    bypass_llm: bool
    emergency_contacts: List[EmergencyContact] = field(default_factory=list)
    crisis_message: Optional[str] = None
    triggered_rules: List[str] = field(default_factory=list)
    audit_logged: bool = False


class SafetyGatekeeper:
    """
    Guarantees no generative AI is invoked during student distress or crisis.
    """

    def __init__(
        self,
        risk_detector: Optional[RiskDetector] = None,
        emergency_handler: Optional[EmergencyHandler] = None,
        audit_logger: Optional[CrisisAuditLogger] = None,
    ) -> None:
        self.risk_detector = risk_detector or RiskDetector()
        self.emergency_handler = emergency_handler or EmergencyHandler()
        self.audit_logger = audit_logger or CrisisAuditLogger()

    def evaluate(
        self,
        query: str,
        session_id: Optional[str] = None,
        university_id: Optional[str] = None,
    ) -> GatekeeperResult:
        """
        Screen query before generative AI.

        Returns GatekeeperResult indicating whether AI pipeline may proceed.
        """
        assessment = self.risk_detector.assess(query)
        final_level = assessment.final_risk_level

        # HIGH and CRITICAL trigger immediate bypass
        if final_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            logger.warning(
                "SAFETY GATEKEEPER TRIGGERED | risk=%s | rules=%s",
                final_level.value,
                len(assessment.triggered_rules),
            )
            contacts = self.emergency_handler.get_critical_contacts_only(university_id)

            # Record audit entry with student message strictly redacted
            self.audit_logger.log_crisis_bypass(
                risk_level=final_level.value,
                category="SELF_HARM_CRISIS",
                session_id=session_id,
                triggered_rules=assessment.triggered_rules,
                raw_message=query,
                contacts_served_count=len(contacts),
            )

            return GatekeeperResult(
                is_safe=False,
                risk_level=final_level,
                bypass_llm=True,
                emergency_contacts=contacts,
                crisis_message=CRISIS_MESSAGE,
                triggered_rules=assessment.triggered_rules,
                audit_logged=True,
            )

        return GatekeeperResult(
            is_safe=True,
            risk_level=final_level,
            bypass_llm=False,
            emergency_contacts=[],
            crisis_message=None,
            triggered_rules=[],
            audit_logged=False,
        )
