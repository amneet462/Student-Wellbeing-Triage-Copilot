"""
app/orchestration/state_machine.py
────────────────────────────────────
Deterministic Triage State Machine.

This module implements the workflow controller for the triage engine.
All state transitions are explicit and rule-driven. No LLM decides the safety flow.

State Transition Diagram
────────────────────────
  RECEIVED
    └──► ANALYZING
           ├──► CRISIS_DETECTED ──► EMERGENCY_RESPONSE  (terminal, no LLM)
           ├──► HUMAN_REVIEW                             (terminal, no LLM)
           ├──► ACADEMIC_SUPPORT                         (can invoke Module 3)
           ├──► EMOTIONAL_SUPPORT                        (can invoke Module 2)
           ├──► FINANCIAL_SUPPORT                        (can invoke Module 3)
           ├──► ADMINISTRATIVE_SUPPORT                   (can invoke Module 3)
           └──► NON_CRISIS                               (can invoke Module 2/3)

Invariants (enforced by this machine)
──────────────────────────────────────
  • CRISIS_DETECTED always transitions to EMERGENCY_RESPONSE.
  • EMERGENCY_RESPONSE and HUMAN_REVIEW never transition to any AI workflow state.
  • Every transition is logged (without raw message text when REDACT_MESSAGE_TEXT=True).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.config import REDACT_MESSAGE_TEXT
from app.schemas.triage_schema import RiskLevel, TriageState

logger = logging.getLogger(__name__)


# ── Transition table ──────────────────────────────────────────────────────────
#
# Format: (from_state, risk_level, category_flag) → to_state
# "category_flag" is a simplified label; routing logic in resource_router.py
# handles the full detail.

_TRANSITIONS: dict[tuple[TriageState, str], TriageState] = {
    (TriageState.RECEIVED, "any"): TriageState.ANALYZING,
    (TriageState.ANALYZING, "CRITICAL"): TriageState.CRISIS_DETECTED,
    (TriageState.ANALYZING, "HIGH"): TriageState.HUMAN_REVIEW,
    (TriageState.ANALYZING, "ACADEMIC"): TriageState.ACADEMIC_SUPPORT,
    (TriageState.ANALYZING, "EMOTIONAL"): TriageState.EMOTIONAL_SUPPORT,
    (TriageState.ANALYZING, "FINANCIAL"): TriageState.FINANCIAL_SUPPORT,
    (TriageState.ANALYZING, "ADMINISTRATIVE"): TriageState.ADMINISTRATIVE_SUPPORT,
    (TriageState.ANALYZING, "GENERAL"): TriageState.NON_CRISIS,
    (TriageState.CRISIS_DETECTED, "any"): TriageState.EMERGENCY_RESPONSE,
}

# States from which NO further autonomous AI workflow transitions are permitted.
_LOCKED_STATES: frozenset[TriageState] = frozenset({
    TriageState.EMERGENCY_RESPONSE,
    TriageState.CRISIS_DETECTED,
    TriageState.HUMAN_REVIEW,
})


@dataclass
class TransitionLog:
    """Immutable record of a single state transition (no raw message content)."""
    session_id: str
    from_state: TriageState
    to_state: TriageState
    trigger: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class TriageSession:
    """
    Tracks the lifecycle of a single triage request through the state machine.

    Fields
    ──────
    session_id   : UUID for this request (safe to log).
    current_state: The machine's current state.
    history      : Ordered list of transition log entries.
    locked       : True if the session is in a safety-locked state.
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_state: TriageState = TriageState.RECEIVED
    history: list[TransitionLog] = field(default_factory=list)
    locked: bool = False


class TriageStateMachine:
    """
    Controls the triage workflow deterministically.

    The machine enforces the invariant that CRITICAL or HIGH-risk sessions
    can never transition into AI-assisted response states.

    Usage
    ─────
    machine = TriageStateMachine()
    session = machine.create_session()
    machine.transition(session, risk_level=RiskLevel.CRITICAL, category_flag="CRITICAL")
    # → session.current_state is TriageState.EMERGENCY_RESPONSE
    # → session.locked is True
    """

    def create_session(self) -> TriageSession:
        """Create a new triage session starting at RECEIVED."""
        session = TriageSession()
        logger.info("[session=%s] Created | state=RECEIVED", session.session_id)
        return session

    def transition(
        self,
        session: TriageSession,
        risk_level: RiskLevel,
        category_flag: str,
        trigger_label: Optional[str] = None,
    ) -> TriageState:
        """
        Advance the state machine based on risk level and category flag.

        Parameters
        ──────────
        session       : The current TriageSession.
        risk_level    : The assessed risk level.
        category_flag : Simplified category tag (e.g. "ACADEMIC", "CRITICAL").
        trigger_label : Human-readable description for log (no message content).

        Returns
        ───────
        The new TriageState after transition.
        """
        if session.locked:
            logger.warning(
                "[session=%s] Transition attempted on locked session (state=%s). Refused.",
                session.session_id,
                session.current_state.value,
            )
            return session.current_state

        # Step 1: RECEIVED → ANALYZING
        if session.current_state == TriageState.RECEIVED:
            self._do_transition(session, TriageState.ANALYZING, trigger_label or "message_received")

        # Step 2: ANALYZING → target state
        if session.current_state == TriageState.ANALYZING:
            target = self._resolve_target(risk_level, category_flag)
            self._do_transition(session, target, trigger_label or f"risk={risk_level.value}")

        # Step 3: If CRISIS_DETECTED, immediately proceed to EMERGENCY_RESPONSE
        if session.current_state == TriageState.CRISIS_DETECTED:
            self._do_transition(session, TriageState.EMERGENCY_RESPONSE, "crisis_protocol")

        # Enforce lock on safety-critical terminal states
        if session.current_state in _LOCKED_STATES:
            session.locked = True
            logger.info(
                "[session=%s] Session locked | state=%s | bypass_llm=True",
                session.session_id,
                session.current_state.value,
            )

        return session.current_state

    def _resolve_target(
        self, risk_level: RiskLevel, category_flag: str
    ) -> TriageState:
        """Map risk level + category to the next state."""
        if risk_level == RiskLevel.CRITICAL:
            return TriageState.CRISIS_DETECTED
        if risk_level == RiskLevel.HIGH:
            return TriageState.HUMAN_REVIEW

        flag_to_state: dict[str, TriageState] = {
            "ACADEMIC": TriageState.ACADEMIC_SUPPORT,
            "EMOTIONAL": TriageState.EMOTIONAL_SUPPORT,
            "FINANCIAL": TriageState.FINANCIAL_SUPPORT,
            "ADMINISTRATIVE": TriageState.ADMINISTRATIVE_SUPPORT,
            "CRISIS": TriageState.HUMAN_REVIEW,
            "GENERAL": TriageState.NON_CRISIS,
        }
        return flag_to_state.get(category_flag.upper(), TriageState.NON_CRISIS)

    def _do_transition(
        self,
        session: TriageSession,
        to_state: TriageState,
        trigger: str,
    ) -> None:
        """Perform and log a state transition."""
        log_entry = TransitionLog(
            session_id=session.session_id,
            from_state=session.current_state,
            to_state=to_state,
            trigger=trigger,
        )
        session.history.append(log_entry)
        logger.info(
            "[session=%s] %s -> %s | trigger='%s'",
            session.session_id,
            session.current_state.value,
            to_state.value,
            trigger,
        )
        session.current_state = to_state

    @staticmethod
    def is_llm_permitted(session: TriageSession) -> bool:
        """
        Returns True ONLY if the current session state allows LLM invocation.

        This is the authoritative check that all calling code must respect.
        """
        return session.current_state not in _LOCKED_STATES

    @staticmethod
    def category_to_flag(category_name: str) -> str:
        """Convert an IssueCategory value string to a simplified flag for the transition table."""
        mapping = {
            "ACADEMIC_STRESS": "ACADEMIC",
            "EMOTIONAL_DISTRESS": "EMOTIONAL",
            "FINANCIAL_PROBLEMS": "FINANCIAL",
            "ADMINISTRATIVE_ISSUES": "ADMINISTRATIVE",
            "SELF_HARM_CRISIS": "CRISIS",
            "GENERAL_QUERY": "GENERAL",
        }
        return mapping.get(category_name, "GENERAL")

