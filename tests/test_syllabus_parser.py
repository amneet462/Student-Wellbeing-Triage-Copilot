"""
tests/test_syllabus_parser.py
──────────────────────────────
Tests for Person 3 Day 2 deliverables:
  1. Syllabus text parsing (Course name, instructor, deliverables)
  2. Decomposed daily 30-minute micro-tasks generation
  3. PDF file upload extraction support
  4. Form and JSON request handling in /api/agent/parse-syllabus
"""

import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.syllabus_parser import extract_text_from_pdf, parse_syllabus_content


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_parse_syllabus_content_text():
    """Verify regex extraction of course, instructor, deliverables, and micro-tasks."""
    sample = (
        "CS301: Advanced Algorithms & Data Structures\n"
        "Instructor: Prof. Evelyn Reed (evelyn.reed@university.edu)\n"
        "Office: Room 402, Turing Building\n"
        "1. Problem Set 1: Graph Algorithms - Due Nov 14, 2026 (20%)\n"
        "2. Midterm Examination - Due Nov 28, 2026 (30%)\n"
        "3. Final Project Report - Due Dec 15, 2026 (50%)\n"
    )

    parsed = parse_syllabus_content(sample)
    assert parsed["status"] == "success"
    assert "CS301" in parsed["course_name"]
    assert "Evelyn Reed" in parsed["professor"]["name"]
    assert "evelyn.reed@university.edu" in parsed["professor"]["email"]
    assert len(parsed["assignments"]) >= 3
    assert len(parsed["generated_tasks"]) >= 4
    assert any("30 min" in t["task"] for t in parsed["generated_tasks"])


def test_parse_syllabus_endpoint_form(client: TestClient):
    """POST /api/agent/parse-syllabus with Form data."""
    res = client.post(
        "/api/agent/parse-syllabus",
        data={"syllabus_text": "MATH201: Calculus III\nProfessor: Dr. Alan Turing (turing@cam.ac.uk)\nMidterm: Nov 20 (40%)"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "MATH201" in data["course_name"]
    assert "Alan Turing" in data["professor"]["name"]
    assert len(data["generated_tasks"]) > 0


def test_parse_syllabus_endpoint_json(client: TestClient):
    """POST /api/agent/parse-syllabus with JSON data."""
    res = client.post(
        "/api/agent/parse-syllabus",
        json={"syllabus_text": "BIO102: Cellular Biology\nInstructor: Prof. Marie Curie\nLab 1: Nov 15 (25%)"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "BIO102" in data["course_name"]


def test_parse_syllabus_endpoint_file_upload(client: TestClient):
    """POST /api/agent/parse-syllabus with uploaded text file."""
    file_content = b"LAW101: Constitutional Law\nProfessor: Dr. Oliver Wendell\nEssay 1: Dec 01 (100%)"
    res = client.post(
        "/api/agent/parse-syllabus",
        files={"file": ("syllabus.txt", io.BytesIO(file_content), "text/plain")}
    )
    assert res.status_code == 200
    data = res.json()
    assert "LAW101" in data["course_name"]
    assert "Oliver Wendell" in data["professor"]["name"]
