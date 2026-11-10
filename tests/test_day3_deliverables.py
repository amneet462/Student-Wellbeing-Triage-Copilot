"""
tests/test_day3_deliverables.py
───────────────────────────────
Comprehensive test suite verifying DAY 3 Key Deliverables & Action Items:

Person 1 (Safety & Triage):
  • /api/resources/campus returning department cards (Financial Aid, Accommodations, Housing)
  • Rate limiting middleware returning 429 when limits are exceeded
  • Global exception handlers preventing 500 crashes and returning safe JSON

Person 2 (RAG Assistant):
  • /api/assistant/cbt-exercises providing structured grounding & breathing exercises
  • Low-confidence similarity fallback check (< 0.60 score) routing to human advisors

Person 3 (Portal & Integration):
  • Calendarized micro-task scheduling (Today / Tomorrow / Next Week)
  • 1-Click Extension Request Email Drafter endpoint (/api/agent/draft-email)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.rate_limiter import SlidingWindowRateLimiter
from app.services.rag.gemini_rag import GeminiRAGAssistant, SIMILARITY_FALLBACK_THRESHOLD


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


# ── Person 1 Tests ────────────────────────────────────────────────────────────

class TestPerson1Day3Deliverables:
    """Verifies Campus Resource Directory, Rate Limiting & Global Exception Handlers."""

    def test_campus_resources_endpoint_departments(self, client: TestClient) -> None:
        """Verify /api/resources/campus returns Financial Aid, Accommodations, and Housing."""
        response = client.get("/api/resources/campus")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["departments"]) >= 3

        categories = [d["category"] for d in data["departments"]]
        assert "FINANCIAL" in categories
        assert "DISABILITY" in categories  # Accommodations
        assert "HOUSING" in categories

        # Verify card details
        for dept in data["departments"]:
            assert "name" in dept
            assert "email" in dept
            assert "phone" in dept
            assert "office" in dept
            assert "hours" in dept
            assert "description" in dept
            assert "services" in dept
            assert len(dept["services"]) > 0

    def test_campus_resources_filtering(self, client: TestClient) -> None:
        """Verify /api/resources/campus supports category query filtering."""
        res_fin = client.get("/api/resources/campus?category=financial")
        assert res_fin.status_code == 200
        data_fin = res_fin.json()
        assert all(d["category"] == "FINANCIAL" for d in data_fin["departments"])

        res_housing = client.get("/api/resources/campus?category=housing")
        assert res_housing.status_code == 200
        data_housing = res_housing.json()
        assert all(d["category"] == "HOUSING" for d in data_housing["departments"])

        res_acc = client.get("/api/resources/campus?category=accommodations")
        assert res_acc.status_code == 200
        data_acc = res_acc.json()
        assert all(d["category"] == "DISABILITY" for d in data_acc["departments"])

    def test_rate_limiter_unit_logic(self) -> None:
        """Direct unit test on SlidingWindowRateLimiter."""
        limiter = SlidingWindowRateLimiter(requests_per_minute=3, window_seconds=60)
        client_ip = "test-client-123"

        # Request 1, 2, 3 should be permitted
        is_lim, rem, _ = limiter.is_rate_limited(client_ip)
        assert is_lim is False
        assert rem == 2

        is_lim, rem, _ = limiter.is_rate_limited(client_ip)
        assert is_lim is False
        assert rem == 1

        is_lim, rem, _ = limiter.is_rate_limited(client_ip)
        assert is_lim is False
        assert rem == 0

        # Request 4 should be blocked with retry-after
        is_lim, rem, retry = limiter.is_rate_limited(client_ip)
        assert is_lim is True
        assert rem == 0
        assert retry > 0

    def test_global_http_exception_handler(self, client: TestClient) -> None:
        """Verify 404/HTTP errors return structured JSON with clinical disclaimer."""
        response = client.get("/api/non-existent-endpoint-xyz")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
        assert "disclaimer" in data


# ── Person 2 Tests ────────────────────────────────────────────────────────────

class TestPerson2Day3Deliverables:
    """Verifies CBT Grounding Exercises API & Low-Confidence Similarity Fallback (< 0.60)."""

    def test_cbt_exercises_endpoint_full_catalog(self, client: TestClient) -> None:
        """Verify /api/assistant/cbt-exercises returns structured grounding & breathing tools."""
        response = client.get("/api/assistant/cbt-exercises")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total"] >= 4

        ex_ids = [e["id"] for e in data["exercises"]]
        assert "grounding_54321" in ex_ids
        assert "box_breathing" in ex_ids
        assert "breathing_478" in ex_ids
        assert "thought_reframing" in ex_ids

        for ex in data["exercises"]:
            assert len(ex["steps"]) >= 3
            assert len(ex["clinical_rationale"]) > 10
            assert ex["duration_min"] > 0
            assert len(ex["target_symptoms"]) > 0

    def test_cbt_exercises_filtering_by_type(self, client: TestClient) -> None:
        """Verify filtering exercises by type (grounding, breathing)."""
        res_grounding = client.get("/api/assistant/cbt-exercises?exercise_type=grounding")
        assert res_grounding.status_code == 200
        assert all(e["type"] == "grounding" for e in res_grounding.json()["exercises"])

        res_breathing = client.get("/api/assistant/cbt-exercises?exercise_type=breathing")
        assert res_breathing.status_code == 200
        assert all(e["type"] == "breathing" for e in res_breathing.json()["exercises"])

    def test_low_confidence_similarity_fallback(self) -> None:
        """Verify queries with similarity < 0.60 trigger human advisor fallback."""
        rag = GeminiRAGAssistant()
        # Query that is completely out of domain
        res = rag.generate_response("what is the exact baking temperature for chocolate chip cookies?")
        assert res.fallback_suggested is True
        assert res.top_similarity < SIMILARITY_FALLBACK_THRESHOLD
        assert "advisor" in res.reply.lower() or "tutor" in res.reply.lower()
        assert res.model_used == "low-similarity-fallback"


# ── Person 3 Tests ────────────────────────────────────────────────────────────

class TestPerson3Day3Deliverables:
    """Verifies Micro-Task Scheduler & 1-Click Extension Request Email Drafter."""

    def test_parse_syllabus_calendarized_tasks(self, client: TestClient) -> None:
        """Verify syllabus parsing generates calendarized micro-tasks (Today, Tomorrow, Next Week)."""
        syllabus = (
            "CS301: Advanced Algorithms & Data Structures\n"
            "Instructor: Prof. Evelyn Reed (evelyn.reed@university.edu)\n"
            "Office: Turing Hall, Room 402\n"
            "1. Problem Set 3: Complexity Analysis - Due Nov 12, 2026 (15%)\n"
            "2. Midterm Examination - Due Nov 20, 2026 (25%)\n"
            "3. Research Project Submission - Due Dec 02, 2026 (40%)\n"
        )
        response = client.post("/api/agent/parse-syllabus", data={"syllabus_text": syllabus})
        assert response.status_code == 200
        data = response.json()

        assert "CS301" in data["course_name"]
        assert len(data["assignments"]) >= 3
        assert len(data["generated_tasks"]) >= 4

        timeframes = [t["timeframe"] for t in data["generated_tasks"]]
        assert "today" in timeframes
        assert "tomorrow" in timeframes
        assert "next_week" in timeframes

        for task in data["generated_tasks"]:
            assert task["estimated_minutes"] in (30, 45)
            assert len(task["task"]) > 10

    def test_extension_email_drafter_endpoint(self, client: TestClient) -> None:
        """Verify /api/agent/draft-email formats polite, policy-compliant email citing §4.3."""
        payload = {
            "course_code": "CS301",
            "professor_name": "Prof. Evelyn Reed",
            "assignment_title": "Problem Set 3: Complexity Analysis",
            "due_date": "Nov 12, 2026",
            "reason": "acute migraine and fever",
            "requested_days": 3,
            "student_name": "Alex Morgan",
            "student_id": "2026-8941",
        }
        response = client.post("/api/agent/draft-email", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Extension Request" in data["subject"]
        assert "CS301" in data["subject"]
        assert "Prof. Evelyn Reed" in data["body"]
        assert "Problem Set 3" in data["body"]
        assert "acute migraine and fever" in data["body"]
        assert "§4.3" in data["policy_cited"] or "Extenuating Circumstances" in data["policy_cited"]
