"""
app/api/agent_routes.py
───────────────────────
FastAPI routes for Productivity Agents: Syllabus De-escalation & Extension Email Drafter.
Initially stubbed with verified mock responses for team development.
"""

from __future__ import annotations

import logging
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, UploadFile, File, Form

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Productivity Agents"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ProfessorInfo(BaseModel):
    name: str = Field(..., description="Faculty or instructor name.")
    email: str = Field(..., description="Faculty contact email.")
    office: Optional[str] = Field(None, description="Office room or hours.")


class AssignmentItem(BaseModel):
    title: str = Field(..., description="Title or description of the coursework.")
    due_date: str = Field(..., description="Due date string (YYYY-MM-DD or text).")
    weight: Optional[str] = Field(None, description="Percentage of final course grade.")


class DecomposedTask(BaseModel):
    day: str = Field(..., description="Target milestone day (e.g. 'Day 1', 'Today').")
    task: str = Field(..., description="Actionable 30-45 minute micro-task description.")
    estimated_minutes: int = Field(30, description="Estimated time required.")


class SyllabusParseResponse(BaseModel):
    status: str
    course_name: str
    professor: ProfessorInfo
    assignments: List[AssignmentItem]
    generated_tasks: List[DecomposedTask]
    notes: Optional[str] = None


class EmailDraftRequest(BaseModel):
    course_code: str = Field(..., description="Course code (e.g. CS101, LAW204).")
    professor_name: str = Field(..., description="Name of professor or module leader.")
    assignment_title: str = Field(..., description="Title of the assignment needing extension.")
    due_date: str = Field(..., description="Current deadline date.")
    reason: str = Field(..., description="Brief reason (e.g. sudden illness, family emergency).")
    requested_days: Optional[int] = Field(3, description="Number of additional days requested.")


class EmailDraftResponse(BaseModel):
    status: str
    subject: str
    body: str
    policy_cited: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/parse-syllabus", response_model=SyllabusParseResponse)
async def parse_syllabus(
    file: Optional[UploadFile] = File(None),
    syllabus_text: Optional[str] = Form(None)
) -> SyllabusParseResponse:
    """
    Syllabus De-escalation Agent (Person 3).
    Extracts course info, assignments, deadlines, and automatically generates
    manageable daily 30-minute micro-tasks.
    """
    filename = file.filename if file else "Text Paste"
    logger.info("Parsing syllabus from: %s", filename)
    
    # Return structured coursework breakdown & micro-tasks
    return SyllabusParseResponse(
        status="success",
        course_name="CS101: Introduction to Computer Systems & Architecture",
        professor=ProfessorInfo(
            name="Dr. Sarah Jenkins",
            email="s.jenkins@university.ac.uk",
            office="Turing Computing Building, Room 302"
        ),
        assignments=[
            AssignmentItem(
                title="Lab 1: Memory Models & Cache Allocation",
                due_date="2026-11-14",
                weight="15%"
            ),
            AssignmentItem(
                title="Midterm Examination (Comprehensive)",
                due_date="2026-11-28",
                weight="35%"
            ),
            AssignmentItem(
                title="Final Term Project & Architecture Report",
                due_date="2026-12-15",
                weight="50%"
            )
        ],
        generated_tasks=[
            DecomposedTask(
                day="Today (Focus 1)",
                task="Review lecture slides on pointers and cache memory models (30 min)",
                estimated_minutes=30
            ),
            DecomposedTask(
                day="Tomorrow (Focus 2)",
                task="Download Lab 1 starter code and verify compilation with GCC (30 min)",
                estimated_minutes=30
            ),
            DecomposedTask(
                day="Day 3 (Focus 3)",
                task="Complete core allocation functions in malloc.c and test suite (45 min)",
                estimated_minutes=45
            ),
            DecomposedTask(
                day="Day 4 (Focus 4)",
                task="Write analysis comments, check memory leaks with Valgrind, and submit (30 min)",
                estimated_minutes=30
            )
        ],
        notes="Syllabus decomposed into 4 daily micro-milestones. Executive panic mitigated."
    )


@router.post("/draft-email", response_model=EmailDraftResponse)
async def draft_extension_email(request: EmailDraftRequest) -> EmailDraftResponse:
    """
    1-Click Extension Request Email Drafter (Person 3).
    Generates a respectful, policy-compliant extension request to faculty.
    """
    logger.info("Drafting extension request for course: %s", request.course_code)
    
    subject = f"Extension Request: {request.assignment_title} ({request.course_code})"
    body = (
        f"Dear {request.professor_name},\n\n"
        f"I hope this message finds you well.\n\n"
        f"I am writing to respectfully request a brief {request.requested_days}-day extension on "
        f"{request.assignment_title} (currently due on {request.due_date}) for {request.course_code}.\n\n"
        f"Unfortunately, I have experienced unexpected difficulties due to {request.reason}, which has "
        f"substantially impacted my ability to complete the work to my usual standard.\n\n"
        f"I am closely following the university's mitigating circumstances guidelines and am prepared "
        f"to submit supporting documentation through the portal. I have already completed substantial "
        f"preparatory work and would be grateful for an adjusted submission deadline.\n\n"
        f"Thank you very much for your time, consideration, and support.\n\n"
        f"Respectfully,\n"
        f"[Student Name]\n"
        f"[Student ID Number]\n"
        f"Department of Computer Science"
    )
    
    return EmailDraftResponse(
        status="success",
        subject=subject,
        body=body,
        policy_cited="University Academic Regulations Handbook 2026 §4.3 (Extenuating Circumstances)"
    )

