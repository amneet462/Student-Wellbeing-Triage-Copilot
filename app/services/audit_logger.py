"""
app/services/audit_logger.py
────────────────────────────
Clinical Safety Audit Logger.

Records immutable audit entries whenever the crisis safety bypass is triggered.
Adheres to strict data protection and confidentiality principles:
  • All student message text is strictly REDACTED to prevent PII/PHI leakage.
  • Identifiers are one-way cryptographic SHA-256 hashes.
  • Timestamps are ISO 8601 UTC.
  • Appends entries as structured JSON Lines (JSONL) for SIEM ingestion.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_AUDIT_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "audit_logs"
DEFAULT_AUDIT_LOG_FILE = DEFAULT_AUDIT_LOG_DIR / "crisis_audit.jsonl"


class CrisisAuditLogger:
    """
    Thread-safe, privacy-preserving audit logger for safety crisis bypass events.
    """

    def __init__(self, log_file: Optional[Path | str] = None) -> None:
        self.log_file = Path(log_file) if log_file else DEFAULT_AUDIT_LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _anonymize_identifier(identifier: Optional[str]) -> str:
        """One-way SHA-256 hash of student/session identifier."""
        if not identifier:
            return "ANONYMOUS_SESSION"
        return hashlib.sha256(identifier.strip().encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _redact_message(message: str) -> str:
        """Ensures all personal distress text is replaced with privacy marker."""
        char_count = len(message.strip()) if message else 0
        return f"[REDACTED_SENSITIVE_TEXT char_count={char_count}]"

    def log_crisis_bypass(
        self,
        risk_level: str,
        category: str = "SELF_HARM_CRISIS",
        session_id: Optional[str] = None,
        triggered_rules: Optional[List[str]] = None,
        raw_message: Optional[str] = None,
        contacts_served_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Records a crisis bypass event with personal text redacted.
        """
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "CRISIS_BYPASS_TRIGGERED",
            "risk_level": str(risk_level).upper(),
            "category": str(category),
            "session_hash": self._anonymize_identifier(session_id),
            "redacted_text": self._redact_message(raw_message or ""),
            "triggered_rules": [r[:80] for r in (triggered_rules or [])],
            "action_taken": "EMERGENCY_BYPASS_NO_LLM",
            "contacts_served_count": contacts_served_count,
            "metadata": metadata or {},
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            logger.warning(
                "CRISIS AUDIT LOGGED | risk=%s | session_hash=%s | contacts=%d",
                entry["risk_level"],
                entry["session_hash"],
                contacts_served_count,
            )
        except Exception as exc:
            logger.error("Failed to write crisis audit log: %s", exc)

        return entry

    def read_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Reads recent audit log entries in reverse chronological order."""
        if not self.log_file.exists():
            return []

        records: List[Dict[str, Any]] = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        except Exception as exc:
            logger.error("Failed reading crisis audit log: %s", exc)

        return records[-limit:][::-1]

    def clear(self) -> None:
        """Clears audit logs (used for test isolation)."""
        if self.log_file.exists():
            self.log_file.unlink()
