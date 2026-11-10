"""
tests/test_campus_directory.py
───────────────────────────────
Tests for Person 1 Day 3 deliverables:
  1. Campus Support Directory endpoint (/api/resources/campus)
  2. Category and keyword search filtering
  3. Contact completeness (Financial Aid, Housing, Disability, Academic, Wellness, Security)
  4. Rate limiting protection (SlidingWindowRateLimiter and RateLimitMiddleware)
  5. Error resilience against malformed inputs
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.rate_limiter import SlidingWindowRateLimiter


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


class TestCampusDirectory:
    """Verifies the campus directory endpoint returns comprehensive student resources."""

    def test_get_all_departments(self, client: TestClient) -> None:
        """GET /api/resources/campus returns all 6 official campus support units."""
        res = client.get("/api/resources/campus")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["total_count"] >= 6
        assert len(data["departments"]) >= 6

    def test_department_fields_complete(self, client: TestClient) -> None:
        """Every department card must have all required contact information."""
        res = client.get("/api/resources/campus")
        data = res.json()
        for dept in data["departments"]:
            assert dept["id"]
            assert dept["name"]
            assert dept["category"] in ("FINANCIAL", "DISABILITY", "HOUSING", "ACADEMIC", "WELLNESS", "SECURITY")
            assert "@" in dept["email"], f"Invalid email in {dept['name']}"
            assert len(dept["phone"]) >= 10, f"Invalid phone in {dept['name']}"
            assert dept["office"]
            assert dept["hours"]
            assert dept["description"]

    @pytest.mark.parametrize("category", ["FINANCIAL", "DISABILITY", "HOUSING", "ACADEMIC", "WELLNESS", "SECURITY"])
    def test_filter_by_category(self, client: TestClient, category: str) -> None:
        """Category query parameter correctly isolates departments."""
        res = client.get(f"/api/resources/campus?category={category}")
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] >= 1
        for dept in data["departments"]:
            assert dept["category"] == category

    def test_search_filter_by_keyword(self, client: TestClient) -> None:
        """Search query 'bursary' returns financial aid; 'shelter' returns housing."""
        res_bursary = client.get("/api/resources/campus?q=bursary")
        assert res_bursary.status_code == 200
        bursary_data = res_bursary.json()
        assert any(d["category"] == "FINANCIAL" for d in bursary_data["departments"])

        res_housing = client.get("/api/resources/campus?q=shelter")
        assert res_housing.status_code == 200
        housing_data = res_housing.json()
        assert any(d["category"] == "HOUSING" for d in housing_data["departments"])

        res_disability = client.get("/api/resources/campus?q=extra%20time")
        assert res_disability.status_code == 200
        disability_data = res_disability.json()
        assert any(d["category"] == "DISABILITY" for d in disability_data["departments"])


class TestRateLimiter:
    """Verifies that sliding window rate limiter protects endpoints from abuse."""

    def test_sliding_window_limiter_logic(self) -> None:
        """Unit test for SlidingWindowRateLimiter."""
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10)
        client_ip = "192.168.1.100"

        # First 3 requests allowed
        for _ in range(3):
            limited, retry_after = limiter.is_rate_limited(client_ip)
            assert limited is False
            assert retry_after == 0

        # 4th request blocked
        limited, retry_after = limiter.is_rate_limited(client_ip)
        assert limited is True
        assert retry_after > 0

        # Different IP not affected
        other_limited, _ = limiter.is_rate_limited("192.168.1.101")
        assert other_limited is False

    def test_rate_limit_exempt_endpoints(self, client: TestClient) -> None:
        """Health and root endpoints must never be blocked by rate limiting."""
        for _ in range(5):
            res = client.get("/api/triage/health")
            assert res.status_code == 200
            assert res.json().get("status") in ("ok", "healthy")


class TestErrorResilience:
    """Verifies server resilience against malformed inputs."""

    def test_oversized_search_string_handled(self, client: TestClient) -> None:
        """Oversized search query (>100 chars) returns 422 rather than 500."""
        huge_q = "a" * 150
        res = client.get(f"/api/resources/campus?q={huge_q}")
        assert res.status_code == 422

    def test_invalid_category_returns_empty_gracefully(self, client: TestClient) -> None:
        """Non-existent category returns empty list without error."""
        res = client.get("/api/resources/campus?category=NON_EXISTENT_CAT")
        assert res.status_code == 200
        data = res.json()
        assert data["total_count"] == 0
        assert data["departments"] == []

