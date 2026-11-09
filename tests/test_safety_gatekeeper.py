"""
tests/test_safety_gatekeeper.py
───────────────────────────────
Unit tests for Person 1 Day 2 deliverables:
  1. Pre-LLM Safety Gatekeeper
  2. Immediate AI shutdown during crisis
  3. Redacted Crisis Audit Logging
"""

import tempfile
from pathlib import Path
import pytest

from app.schemas.triage_schema import RiskLevel
from app.services.audit_logger import CrisisAuditLogger
from app.services.emergency_handler import EmergencyHandler
from app.services.risk_detector import RiskDetector
from app.services.safety_gatekeeper import SafetyGatekeeper


@pytest.fixture
def temp_audit_file(tmp_path: Path):
    return tmp_path / "test_crisis_audit.jsonl"


@pytest.fixture
def gatekeeper(temp_audit_file: Path):
    audit_logger = CrisisAuditLogger(log_file=temp_audit_file)
    detector = RiskDetector()
    emergency_handler = EmergencyHandler()
    return SafetyGatekeeper(
        risk_detector=detector,
        emergency_handler=emergency_handler,
        audit_logger=audit_logger,
    )


def test_safe_query_passes_gatekeeper(gatekeeper: SafetyGatekeeper):
    """Normal academic queries must pass without crisis intervention."""
    res = gatekeeper.evaluate("How do I request a coursework extension for CS101?")
    assert res.is_safe is True
    assert res.bypass_llm is False
    assert res.risk_level in (RiskLevel.LOW, RiskLevel.MODERATE)
    assert len(res.emergency_contacts) == 0
    assert res.audit_logged is False


def test_critical_query_blocked_and_contacts_returned(gatekeeper: SafetyGatekeeper):
    """Acute distress must be blocked immediately, returning verified emergency contacts."""
    res = gatekeeper.evaluate("I cannot take this anymore, I want to end my life tonight", session_id="student-sess-99")
    assert res.is_safe is False
    assert res.bypass_llm is True
    assert res.risk_level == RiskLevel.CRITICAL
    assert len(res.emergency_contacts) > 0
    assert "CLINICAL SAFETY PROTOCOL" in (res.crisis_message or "")
    assert res.audit_logged is True


def test_audit_log_redacts_personal_text(gatekeeper: SafetyGatekeeper, temp_audit_file: Path):
    """Audit logs must record timestamps and risk levels without leaking personal text."""
    secret_text = "I feel so hopeless and I bought pills to overdose"
    res = gatekeeper.evaluate(secret_text, session_id="user-xyz-123")
    assert res.bypass_llm is True

    audit_logger = gatekeeper.audit_logger
    records = audit_logger.read_logs()
    assert len(records) == 1

    entry = records[0]
    assert entry["event_type"] == "CRISIS_BYPASS_TRIGGERED"
    assert entry["risk_level"] in ("HIGH", "CRITICAL")
    assert "timestamp" in entry
    assert secret_text not in entry["redacted_text"]
    assert "[REDACTED_SENSITIVE_TEXT" in entry["redacted_text"]
    assert entry["session_hash"] != "user-xyz-123"
    assert len(entry["session_hash"]) == 16
    assert entry["action_taken"] == "EMERGENCY_BYPASS_NO_LLM"
    assert entry["contacts_served_count"] > 0
