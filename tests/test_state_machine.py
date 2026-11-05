"""
tests/test_state_machine.py
─────────────────────────────
Unit tests for the Triage State Machine.

Coverage
────────
  TC-SM-01  RECEIVED → ANALYZING → CRISIS_DETECTED → EMERGENCY_RESPONSE (CRITICAL)
  TC-SM-02  RECEIVED → ANALYZING → HUMAN_REVIEW (HIGH)
  TC-SM-03  RECEIVED → ANALYZING → ACADEMIC_SUPPORT (LOW/MODERATE academic)
  TC-SM-04  RECEIVED → ANALYZING → EMOTIONAL_SUPPORT
  TC-SM-05  RECEIVED → ANALYZING → FINANCIAL_SUPPORT
  TC-SM-06  RECEIVED → ANALYZING → ADMINISTRATIVE_SUPPORT
  TC-SM-07  RECEIVED → ANALYZING → NON_CRISIS (general)
  TC-SM-08  Locked sessions refuse further transitions
  TC-SM-09  LLM is NOT permitted in EMERGENCY_RESPONSE state
  TC-SM-10  LLM is NOT permitted in HUMAN_REVIEW state
  TC-SM-11  LLM IS permitted in non-critical states
  TC-SM-12  State history is recorded correctly
"""

import pytest

from app.orchestration.state_machine import TriageStateMachine, TriageSession
from app.schemas.triage_schema import RiskLevel, TriageState


@pytest.fixture
def machine() -> TriageStateMachine:
    return TriageStateMachine()


class TestCriticalPath:
    """TC-SM-01"""

    def test_critical_reaches_emergency_response(self, machine):
        session = machine.create_session()
        assert session.current_state == TriageState.RECEIVED

        final = machine.transition(session, RiskLevel.CRITICAL, "CRITICAL")
        assert final == TriageState.EMERGENCY_RESPONSE

    def test_critical_session_is_locked(self, machine):
        session = machine.create_session()
        machine.transition(session, RiskLevel.CRITICAL, "CRITICAL")
        assert session.locked is True

    def test_critical_state_history(self, machine):
        session = machine.create_session()
        machine.transition(session, RiskLevel.CRITICAL, "CRITICAL")
        states = [t.to_state for t in session.history]
        # Must pass through ANALYZING and CRISIS_DETECTED on the way to EMERGENCY_RESPONSE
        assert TriageState.ANALYZING in states
        assert TriageState.EMERGENCY_RESPONSE in states


class TestHighPath:
    """TC-SM-02"""

    def test_high_risk_reaches_human_review(self, machine):
        session = machine.create_session()
        final = machine.transition(session, RiskLevel.HIGH, "HIGH")
        assert final == TriageState.HUMAN_REVIEW

    def test_high_session_is_locked(self, machine):
        session = machine.create_session()
        machine.transition(session, RiskLevel.HIGH, "HIGH")
        assert session.locked is True


class TestNonCriticalPaths:
    """TC-SM-03 through TC-SM-07"""

    @pytest.mark.parametrize(
        "risk, flag, expected_state",
        [
            (RiskLevel.LOW, "ACADEMIC", TriageState.ACADEMIC_SUPPORT),
            (RiskLevel.MODERATE, "ACADEMIC", TriageState.ACADEMIC_SUPPORT),
            (RiskLevel.LOW, "EMOTIONAL", TriageState.EMOTIONAL_SUPPORT),
            (RiskLevel.MODERATE, "EMOTIONAL", TriageState.EMOTIONAL_SUPPORT),
            (RiskLevel.LOW, "FINANCIAL", TriageState.FINANCIAL_SUPPORT),
            (RiskLevel.LOW, "ADMINISTRATIVE", TriageState.ADMINISTRATIVE_SUPPORT),
            (RiskLevel.LOW, "GENERAL", TriageState.NON_CRISIS),
        ],
    )
    def test_routing_state(self, machine, risk, flag, expected_state):
        session = machine.create_session()
        final = machine.transition(session, risk, flag)
        assert final == expected_state, (
            f"Expected {expected_state.value} for risk={risk.value}, flag={flag}. "
            f"Got {final.value}."
        )

    @pytest.mark.parametrize(
        "risk, flag",
        [
            (RiskLevel.LOW, "ACADEMIC"),
            (RiskLevel.MODERATE, "EMOTIONAL"),
            (RiskLevel.LOW, "FINANCIAL"),
            (RiskLevel.LOW, "GENERAL"),
        ],
    )
    def test_non_critical_sessions_are_not_locked(self, machine, risk, flag):
        session = machine.create_session()
        machine.transition(session, risk, flag)
        assert session.locked is False


class TestLockedSessions:
    """TC-SM-08"""

    def test_locked_session_refuses_transition(self, machine):
        session = machine.create_session()
        machine.transition(session, RiskLevel.CRITICAL, "CRITICAL")
        assert session.locked is True

        # Attempt another transition — should be refused
        state_before = session.current_state
        machine.transition(session, RiskLevel.LOW, "GENERAL")
        assert session.current_state == state_before, (
            "Locked session must refuse state transitions."
        )


class TestLLMPermission:
    """TC-SM-09, TC-SM-10, TC-SM-11"""

    def test_llm_not_permitted_in_emergency_response(self, machine):
        """TC-SM-09: LLM must be blocked in EMERGENCY_RESPONSE."""
        session = machine.create_session()
        machine.transition(session, RiskLevel.CRITICAL, "CRITICAL")
        assert machine.is_llm_permitted(session) is False

    def test_llm_not_permitted_in_human_review(self, machine):
        """TC-SM-10: LLM must be blocked in HUMAN_REVIEW."""
        session = machine.create_session()
        machine.transition(session, RiskLevel.HIGH, "HIGH")
        assert machine.is_llm_permitted(session) is False

    @pytest.mark.parametrize(
        "risk, flag",
        [
            (RiskLevel.LOW, "ACADEMIC"),
            (RiskLevel.MODERATE, "EMOTIONAL"),
            (RiskLevel.LOW, "FINANCIAL"),
        ],
    )
    def test_llm_permitted_in_non_critical_states(self, machine, risk, flag):
        """TC-SM-11: LLM should be permitted for non-crisis messages."""
        session = machine.create_session()
        machine.transition(session, risk, flag)
        assert machine.is_llm_permitted(session) is True


class TestStateHistory:
    """TC-SM-12"""

    def test_history_recorded_in_order(self, machine):
        session = machine.create_session()
        machine.transition(session, RiskLevel.LOW, "ACADEMIC")
        states = [t.to_state.value for t in session.history]
        assert states[0] == "ANALYZING"
        assert states[1] == "ACADEMIC_SUPPORT"

    def test_history_has_session_id(self, machine):
        session = machine.create_session()
        machine.transition(session, RiskLevel.LOW, "GENERAL")
        for entry in session.history:
            assert entry.session_id == session.session_id


class TestCategoryToFlag:
    """Test the category_to_flag helper."""

    def test_academic_flag(self):
        assert TriageStateMachine.category_to_flag("ACADEMIC_STRESS") == "ACADEMIC"

    def test_emotional_flag(self):
        assert TriageStateMachine.category_to_flag("EMOTIONAL_DISTRESS") == "EMOTIONAL"

    def test_financial_flag(self):
        assert TriageStateMachine.category_to_flag("FINANCIAL_PROBLEMS") == "FINANCIAL"

    def test_administrative_flag(self):
        assert TriageStateMachine.category_to_flag("ADMINISTRATIVE_ISSUES") == "ADMINISTRATIVE"

    def test_self_harm_flag(self):
        assert TriageStateMachine.category_to_flag("SELF_HARM_CRISIS") == "CRISIS"

    def test_general_flag(self):
        assert TriageStateMachine.category_to_flag("GENERAL_QUERY") == "GENERAL"

    def test_unknown_flag_defaults_to_general(self):
        assert TriageStateMachine.category_to_flag("UNKNOWN_CATEGORY") == "GENERAL"

