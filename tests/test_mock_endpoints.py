"""
tests/test_mock_endpoints.py
────────────────────────────
Integration and contract tests for endpoints provided for team collaboration:
  • /api/assistant/chat          (Dual-Store RAG)
  • /api/assistant/cbt-exercises (CBT Wellness)
  • /api/agent/parse-syllabus    (Syllabus De-escalator)
  • /api/agent/draft-email       (Extension Drafter)
  • /api/resources/campus        (Campus Directory)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Module-scoped FastAPI TestClient fixture."""
    return TestClient(app)


class TestAssistantEndpoints:
    """Tests for AI Assistant & RAG endpoints."""

    def test_chat_returns_citations(self, client: TestClient) -> None:
        """Verify that /api/assistant/chat returns citation-backed responses."""
        response = client.post(
            "/api/assistant/chat",
            json={
                "query": "How do I request an extension for coursework?",
                "session_id": "test-session-001",
                "category": "ACADEMIC_STRESS",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert isinstance(data["reply"], str)
        assert "citations" in data
        assert len(data["citations"]) > 0
        assert "document" in data["citations"][0]
        assert data["safety_checked"] is True

    def test_cbt_exercises_returns_steps(self, client: TestClient) -> None:
        """Verify that /api/assistant/cbt-exercises returns structured exercises."""
        response = client.get("/api/assistant/cbt-exercises")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["exercises"]) >= 2
        assert "steps" in data["exercises"][0]
        assert isinstance(data["exercises"][0]["steps"], list)


class TestAgentEndpoints:
    """Tests for Productivity Agent endpoints."""

    def test_parse_syllabus(self, client: TestClient) -> None:
        """Verify that /api/agent/parse-syllabus extracts coursework and daily micro-tasks."""
        response = client.post(
            "/api/agent/parse-syllabus",
            data={
                "syllabus_text": (
                    "CS101 Intro to Computer Systems. "
                    "Midterm exam on Nov 28. Final Project due Dec 15."
                )
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "course_name" in data
        assert "assignments" in data
        assert len(data["generated_tasks"]) > 0
        assert "task" in data["generated_tasks"][0]

    def test_draft_extension_email(self, client: TestClient) -> None:
        """Verify that /api/agent/draft-email formats a policy-aligned email draft."""
        response = client.post(
            "/api/agent/draft-email",
            json={
                "course_code": "CS101",
                "professor_name": "Dr. Sarah Jenkins",
                "assignment_title": "Lab 1: Memory Models",
                "due_date": "2026-11-14",
                "reason": "medical illness and emergency",
                "requested_days": 3,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Extension Request" in data["subject"]
        assert "Dr. Sarah Jenkins" in data["body"]
        assert "policy_cited" in data


class TestCampusDirectoryEndpoints:
    """Tests for Campus Resource Directory endpoints."""

    def test_get_campus_directory(self, client: TestClient) -> None:
        """Verify that /api/resources/campus returns verified department cards."""
        response = client.get("/api/resources/campus")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["departments"]) >= 3
        categories = [d["category"] for d in data["departments"]]
        assert "FINANCIAL" in categories
        assert "DISABILITY" in categories
        assert "HOUSING" in categories
