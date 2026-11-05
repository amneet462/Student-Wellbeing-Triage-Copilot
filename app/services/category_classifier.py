"""
app/services/category_classifier.py
─────────────────────────────────────
Issue Category Classifier.

Determines which category a student's message belongs to so that it can
be routed to the correct downstream module.

Categories
──────────
  ACADEMIC_STRESS       – Coursework, deadlines, exams, grades, dissertation.
  EMOTIONAL_DISTRESS    – Anxiety, depression, loneliness, burnout, grief.
  FINANCIAL_PROBLEMS    – Fees, loans, bursaries, financial hardship.
  ADMINISTRATIVE_ISSUES – Extensions, accommodation requests, enrolment, disability services.
  SELF_HARM_CRISIS      – Any message already flagged as HIGH/CRITICAL risk.
  GENERAL_QUERY         – Everything else.

The classifier uses a keyword-and-phrase rule set as the primary layer,
supplemented by a TF-IDF + Logistic Regression model trained on seed phrases.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.schemas.triage_schema import IssueCategory, RiskLevel

logger = logging.getLogger(__name__)


# ── Keyword Rule Sets ─────────────────────────────────────────────────────────

_CATEGORY_RULES: dict[IssueCategory, list[re.Pattern]] = {
    IssueCategory.SELF_HARM_CRISIS: [
        re.compile(r"(suicide|suicidal|self[- ]harm|hurt\s+my\s*self|kill\s+my\s*self|"
                   r"end\s+(my|this)\s+life|overdose|cut\s+my\s*self|want\s+to\s+die)", re.I),
    ],
    IssueCategory.ACADEMIC_STRESS: [
        re.compile(r"(exam|assignment|coursework|dissertation|thesis|grade|marks?|"
                   r"deadline|revision|study|lecture|module|essay|project|tutorial|"
                   r"workload|academic|fail(ing)?|pass|professor|lecturer|seminar)", re.I),
    ],
    IssueCategory.FINANCIAL_PROBLEMS: [
        re.compile(r"(fee|tuition|rent|money|financial|loan|bursary|scholarship|"
                   r"afford|pay(ment)?|debt|broke|income|fund|grant|hardship|"
                   r"cannot\s+pay|student\s+finance)", re.I),
    ],
    IssueCategory.ADMINISTRATIVE_ISSUES: [
        re.compile(r"(extension|deferral|accommodation|disability|mitigating|"
                   r"enrol(ment)?|registration|transcript|certificate|appeal|"
                   r"withdraw|interruption|leave\s+of\s+absence|visa|international\s+student|"
                   r"disability\s+services|learning\s+support)", re.I),
    ],
    IssueCategory.EMOTIONAL_DISTRESS: [
        re.compile(r"(anxious|anxiety|depress(ed|ion)?|lonely|loneliness|panic|"
                   r"overwhelm(ed)?|burnout|burned?\s+out|mental\s+health|"
                   r"grief|loss|trauma|stress(ed)?|cope|coping|sad(ness)?|"
                   r"hopeless|worthless|helpless|isolated|sleep|insomnia)", re.I),
    ],
}


# ── Seed Training Data ─────────────────────────────────────────────────────────

_CATEGORY_TRAINING: list[tuple[str, str]] = [
    ("I cannot manage my coursework deadlines", "ACADEMIC_STRESS"),
    ("I am struggling with my dissertation", "ACADEMIC_STRESS"),
    ("I failed my exam and I do not know what to do", "ACADEMIC_STRESS"),
    ("Can I get a coursework extension?", "ADMINISTRATIVE_ISSUES"),
    ("I need an extension for my assignment", "ACADEMIC_STRESS"),
    ("I need disability accommodation", "ADMINISTRATIVE_ISSUES"),
    ("How do I appeal a grade?", "ADMINISTRATIVE_ISSUES"),
    ("I cannot pay my tuition fees this term", "FINANCIAL_PROBLEMS"),
    ("I need information about financial aid and bursaries", "FINANCIAL_PROBLEMS"),
    ("I am in debt and cannot afford food", "FINANCIAL_PROBLEMS"),
    ("I feel very anxious about my exams", "EMOTIONAL_DISTRESS"),
    ("I have been having panic attacks", "EMOTIONAL_DISTRESS"),
    ("I feel so lonely and isolated at university", "EMOTIONAL_DISTRESS"),
    ("I am burned out and exhausted", "EMOTIONAL_DISTRESS"),
    ("I cannot sleep because of anxiety", "EMOTIONAL_DISTRESS"),
    ("I want to kill myself", "SELF_HARM_CRISIS"),
    ("I have been thinking about suicide", "SELF_HARM_CRISIS"),
    ("I am going to hurt myself tonight", "SELF_HARM_CRISIS"),
    ("Where is the student union office?", "GENERAL_QUERY"),
    ("How do I register for classes?", "GENERAL_QUERY"),
    ("What are the library opening hours?", "GENERAL_QUERY"),
]


@dataclass
class CategoryResult:
    """Result of category classification."""
    category: IssueCategory
    confidence: float
    method: str  # "rules" or "ml" or "rules+ml"


class CategoryClassifier:
    """
    Two-stage category classifier.

    Usage
    ─────
    clf = CategoryClassifier()
    result = clf.classify("I cannot pay my tuition fees")
    print(result.category)  # → IssueCategory.FINANCIAL_PROBLEMS
    """

    def __init__(self) -> None:
        self._pipeline: Pipeline | None = None
        self._train()

    def _train(self) -> None:
        try:
            texts = [t for t, _ in _CATEGORY_TRAINING]
            labels = [l for _, l in _CATEGORY_TRAINING]
            self._pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(ngram_range=(1, 3), max_features=800)),
                ("clf", LogisticRegression(max_iter=400, class_weight="balanced", random_state=42)),
            ])
            self._pipeline.fit(texts, labels)
            logger.info("Category classifier trained on %d samples.", len(texts))
        except Exception as exc:
            logger.error("Category classifier training failed: %s", exc)
            self._pipeline = None

    def classify(self, message: str, risk_level: RiskLevel | None = None) -> CategoryResult:
        """
        Classify the message into an issue category.

        If the risk_level is CRITICAL or HIGH, we immediately return
        SELF_HARM_CRISIS without further processing.
        """
        # Safety shortcut: critical/high always maps to crisis category
        if risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH):
            return CategoryResult(
                category=IssueCategory.SELF_HARM_CRISIS,
                confidence=1.0,
                method="rules",
            )

        # Layer 1: keyword rules (deterministic)
        for category, patterns in _CATEGORY_RULES.items():
            for pattern in patterns:
                if pattern.search(message):
                    return CategoryResult(
                        category=category,
                        confidence=0.9,
                        method="rules",
                    )

        # Layer 2: ML classifier
        if self._pipeline is not None:
            try:
                proba = self._pipeline.predict_proba([message])[0]
                classes = self._pipeline.classes_.tolist()
                import numpy as np  # local import to keep top-level clean
                predicted = classes[int(np.argmax(proba))]
                conf = float(np.max(proba))
                return CategoryResult(
                    category=IssueCategory(predicted),
                    confidence=conf,
                    method="ml",
                )
            except Exception as exc:
                logger.warning("Category ML inference failed: %s", exc)

        return CategoryResult(
            category=IssueCategory.GENERAL_QUERY,
            confidence=0.5,
            method="fallback",
        )

