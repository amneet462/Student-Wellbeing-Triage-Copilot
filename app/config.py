"""
app/config.py
─────────────
Central configuration for the Student Wellbeing Triage Engine.

All environment-sensitive values are loaded from environment variables
(with safe defaults for development). Never hard-code secrets here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EMERGENCY_RESOURCES_FILE = DATA_DIR / "emergency_resources.json"

# ── Application ──────────────────────────────────────────────────────────────
APP_TITLE = "AI Student Wellbeing & Triage Copilot – Module 1"
APP_DESCRIPTION = (
    "Risk detection, emergency bypass, and intelligent routing for student wellbeing. "
    "This service is NOT a replacement for professional mental health care."
)
APP_VERSION = "1.0.0"

# ── University / Deployment ──────────────────────────────────────────────────
# Change UNIVERSITY_ID to match a key in emergency_resources.json
UNIVERSITY_ID: str = os.getenv("UNIVERSITY_ID", "default")

# ── Risk & Safety ────────────────────────────────────────────────────────────
# Minimum confidence score (0-1) before the ML classifier can influence routing.
# Safety rules always take precedence over the classifier.
ML_CONFIDENCE_THRESHOLD: float = float(os.getenv("ML_CONFIDENCE_THRESHOLD", "0.65"))

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
# When True, raw message text is NEVER written to logs (recommended for production)
REDACT_MESSAGE_TEXT: bool = os.getenv("REDACT_MESSAGE_TEXT", "true").lower() == "true"

# ── API ──────────────────────────────────────────────────────────────────────
API_PREFIX: str = "/api"
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")

# ── Google Gemini Free Tier ──────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# ── Disclaimer ───────────────────────────────────────────────────────────────
CLINICAL_DISCLAIMER = (
    "This system provides automated initial triage support only. "
    "It does not diagnose mental health conditions, guarantee crisis detection, "
    "or replace professional clinical assessment. "
    "If you are in immediate danger, please call your local emergency services."
)
