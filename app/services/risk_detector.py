"""
app/services/risk_detector.py
──────────────────────────────
Deterministic Safety Detection Engine.

Architecture
────────────
Two-layer approach:

  Layer 1 – Rule-based (DETERMINISTIC, always runs first)
    • Explicit pattern matching using compiled regex rules.
    • Handles direct and indirect self-harm language.
    • Accounts for negations and contextual modifiers.
    • A CRITICAL flag from this layer CANNOT be overridden by anything.

  Layer 2 – ML-assisted (SUPPLEMENTARY, never overrides Layer 1 for CRITICAL)
    • A lightweight TF-IDF + Logistic Regression classifier trained on
      seed phrases for each risk level.
    • Only elevates or supplements the rule-based result.
    • Classifier confidence must exceed ML_CONFIDENCE_THRESHOLD to influence routing.

IMPORTANT LIMITATIONS (always communicated to users):
  • This system does NOT diagnose mental health conditions.
  • A clean scan does NOT guarantee that a student is safe.
  • Ambiguous high-risk messages are escalated to human review.
  • False negatives are possible; this tool augments but cannot replace
    trained human counsellors.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.config import ML_CONFIDENCE_THRESHOLD, REDACT_MESSAGE_TEXT
from app.schemas.triage_schema import RiskLevel

logger = logging.getLogger(__name__)


# ── Rule Patterns ─────────────────────────────────────────────────────────────

# Each pattern is a compiled regex.  Patterns are checked in priority order.
# We use verbose mode (re.VERBOSE) so each rule can be annotated.

_CRITICAL_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE | re.VERBOSE)
    for p in [
        # Direct self-harm intent
        r"(want|going|plan|intend)\s+to\s+(kill|end|take|harm|hurt)\s+(my\s*life|myself|my\s+self|this\s+life)",
        r"\b(?:off|unalive|un-alive)\s+(?:myself|my\s+self)\b",
        r"\b(?:i'?m|i\s+am)\s+done\s+with\s+(?:life|living)\b",
        r"\b(?:i\s+)?(?:want|wanna|going\s+to|gonna|might|plan\s+to)\s+(?:to\s+)?kms\b",
        r"\b(?:took|taken|swallowed|ingested)\s+(?:a\s+)?(?:bunch|handful|lot)\s+of\s+(?:pills|tablets|meds|medication)\b",
        r"(thinking|thought)\s+(about|of)\s+(suicide|killing\s+(myself|my\s*self)|ending\s+(it|my\s*life|everything))",
        r"\b(kill|killing)\s+(myself|my\s*self)\b",
        r"no\s+(reason|point)\s+(for\s+me\s+)?(to\s+(live|continue|go\s+on)|in\s+(living|continuing|going\s+on))",
        r"(suicide|suicidal)\s*(thoughts?|ideation|plan|attempt)",
        r"want\s+to\s+die(\s|$)",
        r"ready\s+to\s+die",
        r"better\s+off\s+(dead|without\s+me)",
        r"no\s+(reason|point)\s+(for\s+me\s+)?to\s+(live|continue|go\s+on)",
        r"(cut|cutting|harm|hurt|injur)\s+(my|your|our)\s*(self|wrist|arm|body|skin)",
        r"\b(overdose|od('?ing)?)\b",
        r"(take|taking|took)\s+(pills|medication)\s+to\s+(end|hurt|kill)",
        # Indirect / contextual crisis language
        r"(everyone\s+(would\s+be\s+better|is\s+better)\s+off\s+without\s+me)",
        r"(nobody|no\s*one)\s+(would|will|cares?)\s+(miss|notice|care)\s+if\s+I",
        r"(saying\s+goodbye|wrote\s+a\s+note|goodbye\s+note|last\s+(message|words?))",
        r"giv(en|ing|e)\s+away\s+(my|all)(\s+(my|all))*\s+(stuff|things|belongings|possessions)",
        r"(end\s+it\s+(all|now)|make\s+it\s+stop\s+permanently)",
        r"(feel\s+(like|that)\s+I('m|\s+am)\s+a\s+burden\s+to\s+(everyone|my\s+family|others?))",
        r"(trapped|stuck)\s+and\s+(see\s+no\s+way\s+out|can'?t\s+(escape|get\s+out))",
    ]
]

_HIGH_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE | re.VERBOSE)
    for p in [
        r"(feel\s+)?(completely\s+)?(hopeless|worthless|helpless)(\s+and\s+(lost|alone|broken))?",
        r"can'?t\s+(go\s+on|keep\s+going|do\s+this\s+anymore|cope\s+anymore)",
        r"(lost\s+all\s+hope|no\s+hope\s+(left|anymore))",
        r"(completely\s+)?broke(n|down)(\s+inside)?",
        r"feel\s+like\s+(I('m|\s+am)\s+)?drowning",
        r"(intense|severe|unbearable|overwhelming)\s+(pain|distress|sadness|despair|suffering)",
        r"(nothing\s+matters?\s+anymore|everything\s+is\s+(pointless|meaningless|useless))",
        r"(wish\s+I\s+(was|were|wasn'?t)\s+(alive|here|born))",
        r"(thoughts?\s+of\s+)?(self[- ]harm|hurting\s+myself)",
        r"(feel\s+)?(completely\s+)?(alone|isolated|abandoned)\s+(and\s+(lost|broken|struggling))?",
        r"(see\s+no\s+way\s+out|(cannot|can'?t)\s+see\s+a\s+way\s+(out|forward)|no\s+way\s+out)",
    ]
]

_MODERATE_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE | re.VERBOSE)
    for p in [
        r"(feel\s+)?(very\s+)?(anxious|depressed|overwhelmed|stressed\s+out)(\s+all\s+the\s+time)?",
        r"(struggling|finding\s+it\s+hard)\s+to\s+(cope|manage|function|sleep|eat)",
        r"(chronic|persistent|constant)\s+(anxiety|worry|fear|sadness)",
        r"(can'?t\s+sleep|unable\s+to\s+sleep|insomnia|sleepless\s+nights?)",
        r"(feeling\s+)?(burned?\s+out|exhausted|drained)\s+emotionally",
        r"(feeling\s+)?low(\s+all\s+the\s+time)?",
        r"(panic\s+attack|panic\s+attacks?)",
        r"(no\s+motivation|lost\s+motivation|can'?t\s+motivate\s+myself)",
        r"(crying\s+(all\s+the\s+time|every\s+day|constantly|a\s+lot))",
        r"(feel\s+)?(really\s+)?(sad|down|miserable)\s+(lately|recently|all\s+the\s+time)?",
    ]
]

# Negation guards: if a matched phrase is immediately preceded by one of these,
# downgrade by one level (but never below the current non-crisis assessment).
_NEGATION_PATTERN = re.compile(
    r"\b(not|never|don'?t|doesn'?t|didn'?t|won'?t|wouldn'?t|no\s+longer|"
    r"without|stopped?|ceased?|past|used\s+to)\b",
    re.IGNORECASE,
)


@dataclass
class RiskAssessment:
    """
    Result object returned by RiskDetector.

    Attributes
    ──────────
    risk_level        : Classified risk tier.
    triggered_rules   : Human-readable labels of the safety rules that fired.
    negation_detected : True when a negation modifier was found near a match.
    ml_risk_level     : Risk level predicted by the ML classifier (may differ from rules).
    ml_confidence     : Classifier confidence (0–1). None if classifier not used.
    final_risk_level  : The authoritative risk level (rules dominate for CRITICAL).
    escalate_to_human : True when ambiguity demands a human reviewer.
    notes             : Non-sensitive explanatory notes for logging.
    """
    risk_level: RiskLevel
    triggered_rules: list[str] = field(default_factory=list)
    negation_detected: bool = False
    ml_risk_level: Optional[RiskLevel] = None
    ml_confidence: Optional[float] = None
    final_risk_level: RiskLevel = RiskLevel.LOW
    escalate_to_human: bool = False
    notes: list[str] = field(default_factory=list)


# ── Seed Training Data for ML Classifier ─────────────────────────────────────
# This is intentionally lightweight; it supplements the rules rather than
# replacing them. In production, replace with a properly validated dataset.

_TRAINING_DATA: list[tuple[str, str]] = [
    # LOW
    ("I am stressed about my exams", "LOW"),
    ("I cannot manage my workload", "LOW"),
    ("I need help with my assignment deadline", "LOW"),
    ("How do I apply for a coursework extension?", "LOW"),
    ("I am struggling with my dissertation", "LOW"),
    ("I cannot pay my tuition fees this semester", "LOW"),
    ("I need information about financial aid", "LOW"),
    ("I need to apply for disability accommodation", "LOW"),
    ("How do I contact the student union?", "LOW"),
    ("I want to change my module", "LOW"),
    ("Where is the library?", "LOW"),
    ("I need study tips for revision", "LOW"),
    # MODERATE
    ("I feel very anxious all the time and I cannot sleep", "MODERATE"),
    ("I am completely overwhelmed and burned out", "MODERATE"),
    ("I am having panic attacks before my exams", "MODERATE"),
    ("I feel so low every day and I have lost all motivation", "MODERATE"),
    ("I am crying constantly and do not know why", "MODERATE"),
    ("I feel isolated and lonely at university", "MODERATE"),
    ("I am struggling to cope with everything", "MODERATE"),
    ("I feel emotionally drained and exhausted", "MODERATE"),
    # HIGH
    ("I feel completely hopeless and I cannot go on like this", "HIGH"),
    ("I feel worthless and nothing matters anymore", "HIGH"),
    ("I feel trapped and I cannot see a way out", "HIGH"),
    ("I wish I was not here anymore", "HIGH"),
    ("I am drowning and I cannot keep going", "HIGH"),
    ("I feel like a burden to everyone around me", "HIGH"),
    ("I have thoughts of self-harm but I have not acted on them", "HIGH"),
    # CRITICAL
    ("I want to kill myself", "CRITICAL"),
    ("I am thinking about suicide", "CRITICAL"),
    ("I want to end my life tonight", "CRITICAL"),
    ("I have been cutting myself", "CRITICAL"),
    ("I am going to hurt myself", "CRITICAL"),
    ("I took an overdose", "CRITICAL"),
    ("I have written a goodbye note", "CRITICAL"),
    ("Everyone would be better off without me and I am ready", "CRITICAL"),
    ("I am giving away all my belongings because I am done", "CRITICAL"),
]


class RiskDetector:
    """
    Two-layer risk detection engine.

    Usage
    ─────
    detector = RiskDetector()
    assessment = detector.assess("I feel hopeless and want to hurt myself")
    print(assessment.final_risk_level)  # → RiskLevel.CRITICAL
    """

    def __init__(self) -> None:
        self._classifier: Optional[Pipeline] = None
        self._train_classifier()

    def _train_classifier(self) -> None:
        """Train the lightweight TF-IDF + Logistic Regression classifier."""
        try:
            texts = [t for t, _ in _TRAINING_DATA]
            labels = [l for _, l in _TRAINING_DATA]
            self._classifier = Pipeline([
                ("tfidf", TfidfVectorizer(
                    ngram_range=(1, 3),
                    max_features=1000,
                    sublinear_tf=True,
                )),
                ("clf", LogisticRegression(
                    max_iter=500,
                    class_weight="balanced",
                    random_state=42,
                )),
            ])
            self._classifier.fit(texts, labels)
            logger.info("Risk classifier trained successfully on %d samples.", len(texts))
        except Exception as exc:
            logger.error("Classifier training failed: %s. Rules-only mode active.", exc)
            self._classifier = None

    # ── Public API ────────────────────────────────────────────────────────────

    def assess(self, message: str) -> RiskAssessment:
        """
        Perform a full risk assessment of the student's message.

        The safety rules are always evaluated first.  CRITICAL rule matches
        are authoritative and cannot be downgraded by the ML layer.

        Parameters
        ──────────
        message : Raw student message text.

        Returns
        ───────
        RiskAssessment dataclass with all relevant fields populated.
        """
        redacted = "[REDACTED]" if REDACT_MESSAGE_TEXT else message
        logger.debug("Assessing message: %s", redacted)

        assessment = RiskAssessment(risk_level=RiskLevel.LOW)

        # ── Layer 1: Deterministic Rules ─────────────────────────────────────
        rule_level, triggered, negation = self._apply_rules(message)
        assessment.risk_level = rule_level
        assessment.triggered_rules = triggered
        assessment.negation_detected = negation

        # ── Layer 2: ML Classifier ───────────────────────────────────────────
        if self._classifier is not None:
            ml_level, ml_conf = self._run_classifier(message)
            assessment.ml_risk_level = ml_level
            assessment.ml_confidence = ml_conf
        else:
            assessment.ml_risk_level = rule_level
            assessment.ml_confidence = None

        # ── Merge: Rules dominate for CRITICAL ───────────────────────────────
        assessment.final_risk_level = self._merge(
            rule_level,
            assessment.ml_risk_level,
            assessment.ml_confidence or 0.0,
        )

        # ── Escalation decision ───────────────────────────────────────────────
        # Escalate when: HIGH level, or ML and rules disagree at HIGH+, or
        # negation was detected alongside HIGH+ rule match.
        if assessment.final_risk_level == RiskLevel.HIGH:
            assessment.escalate_to_human = True
            assessment.notes.append(
                "HIGH risk detected – routed for human review as a precaution."
            )
        if assessment.negation_detected and rule_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            assessment.escalate_to_human = True
            assessment.notes.append(
                "Negation modifier detected near high-risk phrase – escalating for human review."
            )
        if (
            assessment.ml_risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
            and rule_level in (RiskLevel.LOW, RiskLevel.MODERATE)
            and (assessment.ml_confidence or 0.0) >= ML_CONFIDENCE_THRESHOLD
        ):
            assessment.escalate_to_human = True
            assessment.notes.append(
                "ML classifier flagged elevated risk not captured by rules – escalating."
            )

        logger.info(
            "Risk assessment complete | rule=%s | ml=%s | final=%s | escalate=%s",
            rule_level.value,
            assessment.ml_risk_level.value if assessment.ml_risk_level else "N/A",
            assessment.final_risk_level.value,
            assessment.escalate_to_human,
        )

        return assessment

    # ── Private Helpers ───────────────────────────────────────────────────────

    def _apply_rules(
        self, message: str
    ) -> tuple[RiskLevel, list[str], bool]:
        """
        Apply deterministic regex rules in priority order.

        Returns (risk_level, triggered_rule_labels, negation_found).
        """
        triggered: list[str] = []
        negation_found = False

        # Check CRITICAL first
        for pattern in _CRITICAL_PATTERNS:
            match = pattern.search(message)
            if match:
                triggered.append(f"CRITICAL: {pattern.pattern[:60]}...")
                # Even if negation present, CRITICAL stays CRITICAL
                # (better safe than sorry – human will review)
                neg = self._negation_near(message, match)
                if neg:
                    negation_found = True
                return RiskLevel.CRITICAL, triggered, negation_found

        # Check HIGH
        for pattern in _HIGH_PATTERNS:
            match = pattern.search(message)
            if match:
                triggered.append(f"HIGH: {pattern.pattern[:60]}...")
                neg = self._negation_near(message, match)
                if neg:
                    negation_found = True
                    # Negation detected → downgrade to MODERATE but still escalate
                    return RiskLevel.MODERATE, triggered, negation_found
                return RiskLevel.HIGH, triggered, negation_found

        # Check MODERATE
        for pattern in _MODERATE_PATTERNS:
            match = pattern.search(message)
            if match:
                triggered.append(f"MODERATE: {pattern.pattern[:60]}...")
                neg = self._negation_near(message, match)
                if neg:
                    negation_found = True
                    return RiskLevel.LOW, triggered, negation_found
                return RiskLevel.MODERATE, triggered, negation_found

        return RiskLevel.LOW, [], False

    @staticmethod
    def _negation_near(message: str, match: re.Match, window: int = 60) -> bool:
        """
        Check whether a negation word appears within `window` characters
        before the start of the matched phrase.
        """
        start = max(0, match.start() - window)
        preceding = message[start:match.start()]
        return bool(_NEGATION_PATTERN.search(preceding))

    def _run_classifier(self, message: str) -> tuple[RiskLevel, float]:
        """Run the ML classifier and return (predicted_level, confidence)."""
        try:
            proba = self._classifier.predict_proba([message])[0]  # type: ignore[union-attr]
            classes: list[str] = self._classifier.classes_.tolist()  # type: ignore[union-attr]
            predicted_label = classes[int(np.argmax(proba))]
            confidence = float(np.max(proba))
            return RiskLevel(predicted_label), confidence
        except Exception as exc:
            logger.warning("Classifier inference failed: %s", exc)
            return RiskLevel.LOW, 0.0

    @staticmethod
    def _merge(
        rule_level: RiskLevel,
        ml_level: Optional[RiskLevel],
        ml_confidence: float,
    ) -> RiskLevel:
        """
        Merge rule-based and ML results.

        Rules:
         1. CRITICAL from rules → always CRITICAL (no override).
         2. If ML confidence < threshold → trust rules alone.
         3. Otherwise → take the higher of the two levels.
        """
        # Safety rule: CRITICAL is immutable
        if rule_level == RiskLevel.CRITICAL:
            return RiskLevel.CRITICAL

        if ml_level is None or ml_confidence < ML_CONFIDENCE_THRESHOLD:
            return rule_level

        # Rank the levels for comparison
        order = [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]
        rule_rank = order.index(rule_level)
        ml_rank = order.index(ml_level)

        return order[max(rule_rank, ml_rank)]
