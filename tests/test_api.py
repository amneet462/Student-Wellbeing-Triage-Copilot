"""
tests/test_api.py
──────────────────
Integration tests for all API endpoints.

Coverage
────────
  TC-API-01  POST /api/triage/analyze – normal academic stress
  TC-API-02  POST /api/triage/analyze – exam anxiety
  TC-API-03  POST /api/triage/analyze – financial difficulties
  TC-API-04  POST /api/triage/analyze – administrative query
  TC-API-05  POST /api/triage/analyze – explicit self-harm (bypass verified)
  TC-API-06  POST /api/triage/analyze – indirect hopelessness
  TC-API-07  POST /api/triage/analyze – empty message (validation error)
  TC-API-08  POST /api/triage/analyze – whitespace-only message (validation error)
  TC-API-09  POST /api/triage/analyze – oversized message (validation error)
  TC-API-10  POST /api/triage/emergency – returns resource list
  TC-API-11  GET  /api/triage/health – service is healthy
  TC-API-12  GET  /api/triage/categories – returns taxonomy
  TC-API-13  Response schema is complete (all required fields present)
  TC-API-14  Disclaimer is always included in responses
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


class TestHealthAndCategories:
    """TC-API-11, TC-API-12"""

    def test_health_check_returns_ok(self, client):
        """TC-API-11: Health endpoint must return status=ok."""
        response = client.get("/api/triage/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "disclaimer" in data

    def test_categories_endpoint(self, client):
        """TC-API-12: Categories endpoint returns full taxonomy."""
        response = client.get("/api/triage/categories")
        assert response.status_code == 200
        data = response.json()
        assert "risk_levels" in data
        assert "categories" in data
        assert "states" in data
        assert "next_actions" in data
        # Verify all risk levels are present
        for level in ("LOW", "MODERATE", "HIGH", "CRITICAL"):
            assert level in data["risk_levels"]


class TestNormalMessages:
    """TC-API-01 through TC-API-04"""

    def test_academic_stress(self, client):
        """TC-API-01: Academic stress → LOW/MODERATE, academic category."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I am stressed about my upcoming exams."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ("LOW", "MODERATE")
        assert data["emergency"] is False
        assert data["bypass_llm"] is False
        assert data["category"] in ("ACADEMIC_STRESS", "EMOTIONAL_DISTRESS", "GENERAL_QUERY")

    def test_exam_anxiety(self, client):
        """TC-API-02: Exam anxiety → MODERATE, appropriate routing."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I am unable to sleep because of anxiety about my exams."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["emergency"] is False

    def test_financial_difficulties(self, client):
        """TC-API-03: Financial concern → financial routing."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I cannot afford to pay my tuition fees this semester."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["emergency"] is False
        assert data["category"] in ("FINANCIAL_PROBLEMS", "GENERAL_QUERY")

    def test_administrative_query(self, client):
        """TC-API-04: Admin query → administrative routing."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I need to apply for a disability accommodation."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["emergency"] is False
        assert data["category"] in ("ADMINISTRATIVE_ISSUES", "GENERAL_QUERY")


class TestHighRiskMessages:
    """TC-API-06"""

    def test_indirect_hopelessness(self, client):
        """TC-API-06: Indirect hopelessness → at least HIGH, human review."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I feel completely hopeless and I cannot go on like this."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ("HIGH", "CRITICAL")
        assert data["bypass_llm"] is True

    def test_worthless_and_lost(self, client):
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I feel worthless and totally lost. Nothing matters anymore."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ("HIGH", "CRITICAL")


class TestCriticalMessages:
    """TC-API-05"""

    def test_explicit_self_harm(self, client):
        """TC-API-05: Explicit self-harm → CRITICAL, emergency bypass."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I feel hopeless and want to hurt myself."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "CRITICAL"
        assert data["emergency"] is True
        assert data["bypass_llm"] is True
        assert data["state"] == "EMERGENCY_RESPONSE"
        assert data["next_action"] == "EMERGENCY_SUPPORT"


class TestInputValidation:
    """TC-API-07, TC-API-08, TC-API-09"""

    def test_empty_message_rejected(self, client):
        """TC-API-07: Empty message string must return 422 validation error."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": ""},
        )
        assert response.status_code == 422

    def test_whitespace_only_message_rejected(self, client):
        """TC-API-08: Whitespace-only message must return 422 validation error."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "   \n\t  "},
        )
        assert response.status_code == 422

    def test_oversized_message_rejected(self, client):
        """TC-API-09: Message exceeding 2000 chars must return 422 validation error."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "x" * 2001},
        )
        assert response.status_code == 422

    def test_missing_message_field(self, client):
        """Missing required 'message' field → 422."""
        response = client.post(
            "/api/triage/analyze",
            json={"student_id": "anon-001"},
        )
        assert response.status_code == 422


class TestResponseSchema:
    """TC-API-13, TC-API-14"""

    def test_response_has_all_required_fields(self, client):
        """TC-API-13: Every response must include all required schema fields."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I need help with my assignment."},
        )
        assert response.status_code == 200
        data = response.json()
        required_fields = [
            "risk_level",
            "category",
            "state",
            "emergency",
            "bypass_llm",
            "next_action",
            "message",
            "disclaimer",
            "resources",
            "routing_metadata",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: '{field}'"

    def test_disclaimer_always_present(self, client):
        """TC-API-14: Clinical disclaimer must always be included in responses."""
        messages = [
            "I am stressed about my exams.",
            "I want to end my life.",
            "I need help paying my fees.",
        ]
        for msg in messages:
            response = client.post(
                "/api/triage/analyze",
                json={"message": msg},
            )
            data = response.json()
            assert "disclaimer" in data, f"Disclaimer missing for message: {msg!r}"
            assert len(data["disclaimer"]) > 0

    def test_risk_level_is_valid_enum(self, client):
        """Risk level in response must be a valid enum value."""
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I am struggling with my studies."},
        )
        data = response.json()
        assert data["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")

    def test_next_action_is_valid_enum(self, client):
        """next_action must be a valid NextAction value."""
        valid_actions = {
            "EMERGENCY_SUPPORT", "HUMAN_COUNSELLOR", "WORKLOAD_AGENT",
            "WELLNESS_RAG", "FINANCIAL_AID", "DISABILITY_SERVICES",
            "ACADEMIC_SUPPORT", "GENERAL_INFO", "HUMAN_REVIEW",
        }
        response = client.post(
            "/api/triage/analyze",
            json={"message": "I am struggling with my studies."},
        )
        data = response.json()
        assert data["next_action"] in valid_actions


class TestRootAndDocs:
    """Basic smoke tests."""

    def test_root_returns_service_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        # Accepts either the HTML dashboard or the JSON metadata fallback
        if "text/html" in response.headers.get("content-type", ""):
            assert "<!DOCTYPE html>" in response.text
            assert "Student Wellbeing" in response.text
        else:
            data = response.json()
            assert "service" in data
            assert "version" in data
            assert "docs" in data

