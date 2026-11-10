"""
tests/test_cbt_exercises.py
───────────────────────────
Tests for Person 2 Day 3 CBT endpoints:
  • /api/assistant/cbt-exercises
  • /api/assistant/cbt/478-breathing
  • /api/assistant/cbt/54321-grounding
  • /api/assistant/cbt/box-breathing
  • /api/assistant/cbt/progressive-muscle-relaxation
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


class TestCBTInteractiveEndpoints:
    """Tests verifying interactive CBT and somatic pacing endpoints."""

    def test_cbt_exercises_list(self, client: TestClient) -> None:
        """GET /api/assistant/cbt-exercises returns full list of structured exercises."""
        res = client.get("/api/assistant/cbt-exercises")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert len(data["exercises"]) >= 3
        for ex in data["exercises"]:
            assert ex["id"]
            assert ex["name"]
            assert ex["duration_min"] > 0
            assert len(ex["steps"]) > 0
            assert ex["clinical_rationale"]

    def test_478_breathing_protocol(self, client: TestClient) -> None:
        """GET /api/assistant/cbt/478-breathing returns 4s Inhale, 7s Hold, 8s Exhale protocol."""
        res = client.get("/api/assistant/cbt/478-breathing")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == "breathing_478"
        assert data["total_cycles"] == 4
        assert data["cycle_duration_seconds"] == 19
        assert len(data["phases"]) == 3

        phases = {p["phase_name"]: p["duration_seconds"] for p in data["phases"]}
        assert phases["Inhale"] == 4
        assert phases["Hold"] == 7
        assert phases["Exhale"] == 8
        assert "vagus" in data["clinical_rationale"].lower()

    def test_54321_grounding_protocol(self, client: TestClient) -> None:
        """GET /api/assistant/cbt/54321-grounding returns 5 sensory de-escalation steps."""
        res = client.get("/api/assistant/cbt/54321-grounding")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == "grounding_54321"
        assert len(data["steps"]) == 5

        counts = [s["count"] for s in data["steps"]]
        assert counts == [5, 4, 3, 2, 1]
        assert "sight" in data["steps"][0]["sense"].lower()
        assert "touch" in data["steps"][1]["sense"].lower()
        assert "hearing" in data["steps"][2]["sense"].lower()
        assert "smell" in data["steps"][3]["sense"].lower()
        assert "taste" in data["steps"][4]["sense"].lower() or "breath" in data["steps"][4]["sense"].lower()

    def test_box_breathing_protocol(self, client: TestClient) -> None:
        """GET /api/assistant/cbt/box-breathing returns 4-4-4-4 square breathing."""
        res = client.get("/api/assistant/cbt/box-breathing")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == "box_breathing"
        assert data["total_cycles"] == 4
        assert data["cycle_duration_seconds"] == 16
        assert len(data["phases"]) == 4
        for phase in data["phases"]:
            assert phase["duration_seconds"] == 4

    def test_pmr_protocol(self, client: TestClient) -> None:
        """GET /api/assistant/cbt/progressive-muscle-relaxation returns 5 muscle groups."""
        res = client.get("/api/assistant/cbt/progressive-muscle-relaxation")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == "pmr_protocol"
        assert len(data["steps"]) >= 5
        for step in data["steps"]:
            assert step["muscle_group"]
            assert step["tension_seconds"] >= 5
            assert step["release_seconds"] >= 10
            assert step["instruction"]

