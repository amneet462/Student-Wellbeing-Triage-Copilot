"""
tests/test_frontend_integration.py
───────────────────────────────────
Integration tests verifying React Frontend deployment and API contract connectivity.
"""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


class TestFrontendServing:
    """Verifies that the React + Vite frontend build is properly served by FastAPI."""

    def test_root_serves_react_html(self, client: TestClient) -> None:
        """GET / should serve the React SPA index.html."""
        res = client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers.get("content-type", "")
        assert '<div id="root"></div>' in res.text
        assert "Student Wellbeing & Triage Copilot" in res.text

    def test_frontend_can_access_health_endpoint(self, client: TestClient) -> None:
        """React app polls /api/triage/health for status indicator."""
        res = client.get("/api/triage/health")
        assert res.status_code == 200
        data = res.json()
        assert data.get("status") in ("ok", "healthy")

    def test_frontend_can_trigger_triage(self, client: TestClient) -> None:
        """Chat tab posts to /api/triage/analyze for real-time safety gating."""
        payload = {
            "message": "I am struggling with my coursework deadline due to illness",
            "session_id": "test-session-web"
        }
        res = client.post("/api/triage/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "risk_level" in data
        assert "category" in data
        assert str(data["risk_level"]).lower() == "low"
        assert "academic" in str(data["category"]).lower()

    def test_frontend_crisis_triggers_emergency_bypass(self, client: TestClient) -> None:
        """Chat tab verifies that crisis messages set bypass_llm: True for immediate modal pop."""
        payload = {
            "message": "I want to end my life, please help me",
            "session_id": "test-session-crisis"
        }
        res = client.post("/api/triage/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert str(data["risk_level"]).lower() in ("high", "critical")
        assert data["emergency"] is True
        assert data["bypass_llm"] is True
        assert data["routing_metadata"]["llm_invocation_count"] == 0

    def test_frontend_can_fetch_campus_directory(self, client: TestClient) -> None:
        """Resources tab connects to /api/resources/campus."""
        res = client.get("/api/resources/campus")
        assert res.status_code == 200
        data = res.json()
        assert "departments" in data or "resources" in data
        items = data.get("departments") or data.get("resources")
        assert len(items) >= 3
