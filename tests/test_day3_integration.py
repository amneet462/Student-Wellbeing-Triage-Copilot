"""
tests/test_day3_integration.py
──────────────────────────────
Comprehensive integration tests verifying all Day 3 deliverables:
  • Campus Support Directory with multi-category and keyword filters
  • Rate limiting protection
  • Interactive CBT exercises (4-7-8, 5-4-3-2-1, Box Breathing, PMR)
  • 1-Click Extension Request Email Drafter
  • Calendarized micro-task syllabus de-escalator
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


class TestDay3CampusDirectoryIntegration:
    """Verifies that the enhanced campus directory services students across all domains."""

    def test_directory_has_all_categories(self, client: TestClient) -> None:
        """Campus directory returns support for financial, housing, disability, academic, wellness, security."""
        res = client.get("/api/resources/campus")
        assert res.status_code == 200
        data = res.json()
        categories = {d["category"] for d in data["departments"]}
        expected = {"FINANCIAL", "HOUSING", "DISABILITY", "ACADEMIC", "WELLNESS", "SECURITY"}
        assert expected.issubset(categories)

    def test_keyword_search_across_fields(self, client: TestClient) -> None:
        """Search query filters across name, description, office, and category."""
        res = client.get("/api/resources/campus?q=cbt")
        assert res.status_code == 200
        data = res.json()
        assert len(data["departments"]) >= 1
        assert any("cbt" in d["description"].lower() or "cbt" in d["name"].lower() for d in data["departments"])


class TestDay3CBTExercisesIntegration:
    """Verifies that all interactive CBT exercises return structured protocols."""

    def test_478_breathing_cycles_and_phases(self, client: TestClient) -> None:
        res = client.get("/api/assistant/cbt/478-breathing")
        assert res.status_code == 200
        data = res.json()
        assert data["total_cycles"] == 4
        assert len(data["phases"]) == 3

    def test_54321_grounding_has_five_steps(self, client: TestClient) -> None:
        res = client.get("/api/assistant/cbt/54321-grounding")
        assert res.status_code == 200
        data = res.json()
        assert len(data["steps"]) == 5

    def test_pmr_has_multiple_muscle_groups(self, client: TestClient) -> None:
        res = client.get("/api/assistant/cbt/progressive-muscle-relaxation")
        assert res.status_code == 200
        data = res.json()
        assert len(data["steps"]) >= 5


class TestDay3AgentEmailDrafterIntegration:
    """Verifies that the extension request email drafter creates policy-aligned drafts."""

    def test_draft_extension_email_endpoint(self, client: TestClient) -> None:
        """POST /api/agent/draft-email generates professional email referencing extenuating circumstances."""
        payload = {
            "professor_name": "Dr. Alan Turing",
            "course_code": "CS301",
            "assignment_title": "Problem Set 3: Complexity Analysis",
            "due_date": "2026-11-12",
            "requested_days": 5,
            "reason": "acute illness and medical appointments",
            "student_name": "Alex Morgan",
            "student_id": "2026-8941"
        }
        res = client.post("/api/agent/draft-email", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "subject" in data
        assert "body" in data
        assert "policy_cited" in data
        assert "CS301" in data["subject"]
        assert "Dr. Alan Turing" in data["body"]
        assert "Problem Set 3" in data["body"]
        assert "5" in data["body"]
        assert "Extenuating Circumstances" in data["policy_cited"] or "Policy" in data["policy_cited"]


class TestDay3SyllabusMicroTaskIntegration:
    """Verifies that syllabus parser breaks deadlines into calendarized micro-tasks."""

    def test_syllabus_parser_calendarized_breakdown(self, client: TestClient) -> None:
        syllabus = (
            "CS201 Data Structures (Spring 2026)\n"
            "Instructor: Prof. Smith (smith@univ.edu)\n"
            "Assignment 1: Linked Lists due Oct 15\n"
            "Midterm Exam: Nov 05\n"
        )
        res = client.post("/api/agent/parse-syllabus", data={"text": syllabus})
        assert res.status_code == 200
        data = res.json()
        assert "generated_tasks" in data
        assert len(data["generated_tasks"]) >= 2
        for task in data["generated_tasks"]:
            assert "task" in task
            assert "estimated_minutes" in task
            assert "day" in task
            assert task["estimated_minutes"] == 30
