"""
app/api/resource_routes.py
──────────────────────────
FastAPI routes for Campus Department Support Services Directory.
Provides comprehensive contact information, emergency phone lines,
and direct self-service referral links for non-clinical student inquiries.
"""

from __future__ import annotations

import logging
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resources", tags=["Campus Resources"])


class DepartmentCard(BaseModel):
    id: str = Field(..., description="Unique department identifier.")
    name: str = Field(..., description="Official university department name.")
    category: str = Field(..., description="FINANCIAL | DISABILITY | HOUSING | ACADEMIC | WELLNESS | SECURITY")
    email: str = Field(..., description="Official contact email.")
    phone: str = Field(..., description="Direct helpline or desk phone.")
    office: str = Field(..., description="Physical campus building and room location.")
    hours: str = Field(..., description="Operating hours and drop-in schedule.")
    description: str = Field(..., description="Comprehensive scope of department support.")
    services: List[str] = Field(default_factory=list, description="List of primary services provided.")
    action_url: Optional[str] = Field(None, description="Direct web portal link.")
    urgent_support: bool = False


class CampusDirectoryResponse(BaseModel):
    status: str = Field("success", description="Response status.")
    total: int = Field(..., description="Number of departments returned.")
    total_count: Optional[int] = Field(None, description="Alias for total.")
    departments: List[DepartmentCard] = Field(default_factory=list, description="List of department support cards.")

    def model_post_init(self, __context) -> None:
        if self.total_count is None:
            self.total_count = self.total


CAMPUS_DEPARTMENTS: List[DepartmentCard] = [
    DepartmentCard(
        id="financial_aid",
        name="Student Financial Hardship & Emergency Bursary Desk",
        category="FINANCIAL",
        email="student.funding@university.ac.uk",
        phone="0800 028 4455",
        office="Student Central Building, Ground Floor Suite 10",
        hours="Mon–Fri 9:00am–4:30pm",
        description="Emergency living bursaries, short-term interest-free crisis loans, food vouchers, and tuition fee instalment deferrals.",
        services=[
            "Emergency Non-Repayable Hardship Grants (up to £1,500)",
            "Interest-Free Short-Term Crisis Loans",
            "Tuition Fee Deferral & Payment Plan Restructuring",
            "Digital Poverty Tech Bursary (Laptops & Wi-Fi Dongles)",
        ],
        action_url="https://students.university.ac.uk/financial-aid",
        urgent_support=False,
    ),
    DepartmentCard(
        id="disability_services",
        name="Disability, Neurodiversity & Inclusion Team",
        category="DISABILITY",
        email="disability.support@university.ac.uk",
        phone="0800 028 7788",
        office="Wilkins Building, Room 102",
        hours="Mon–Fri 8:30am–5:00pm",
        description="Reasonable exam adjustments, 25% extra time arrangements, assistive software licences, rest break passes, and sensory room access.",
        services=[
            "Summary of Reasonable Adjustments (SoRA)",
            "25% Extra Time & Rest Breaks in Examinations",
            "Assistive Technology Software & Ergonomic Equipment",
            "Dedicated Specialist Study Skills & Mental Health Mentors",
        ],
        action_url="https://students.university.ac.uk/disability",
        urgent_support=False,
    ),
    DepartmentCard(
        id="emergency_housing",
        name="Student Housing Advisory & Emergency Shelter",
        category="HOUSING",
        email="housing.advice@university.ac.uk",
        phone="0800 028 9911",
        office="Campus Living Pavilion, Desk B",
        hours="24/7 Crisis Dispatch & Weekdays 9:00am–5:00pm",
        description="Immediate emergency temporary shelter, private tenancy disputes, rent guarantor schemes, and deposit dispute resolution.",
        services=[
            "Immediate Emergency Safe Shelter Placement (Same-Day)",
            "Private Tenancy Contract Review & Dispute Resolution",
            "University Rent Guarantor Scheme for International Students",
            "Deposit Protection & Housing Standard Inspections",
        ],
        action_url="https://students.university.ac.uk/housing",
        urgent_support=True,
    ),
    DepartmentCard(
        id="academic_advice",
        name="Student Union Independent Academic Advice",
        category="ACADEMIC",
        email="academic.advice@su.university.ac.uk",
        phone="0800 028 3344",
        office="Student Union Building, Floor 1",
        hours="Mon–Fri 9:30am–4:00pm",
        description="Confidential student advocacy, academic appeals, disciplinary hearing representation, and course withdrawal/deferral guidance.",
        services=[
            "Extenuating Circumstances Policy Evidence Guidance (§4.3)",
            "Formal Academic Appeals & Grade Dispute Representation",
            "Independent Representation in Misconduct Hearings",
            "Interruption of Studies & Course Transfer Advising",
        ],
        action_url="https://su.university.ac.uk/advice",
        urgent_support=False,
    ),
    DepartmentCard(
        id="mental_health_hub",
        name="Student Mental Health & Psychological Wellbeing Hub",
        category="WELLNESS",
        email="counselling.hub@university.ac.uk",
        phone="0800 028 3766",
        office="Wellbeing Centre, Ground Floor",
        hours="Mon–Fri 8:30am–5:30pm (Same-day duty triage appointments daily)",
        description="Free short-term CBT counselling, structured anxiety workshops, guided somatic meditation sessions, and duty clinician drop-ins.",
        services=[
            "Free Short-Term CBT & Psychological Counselling",
            "Structured Anxiety, Stress & Low Mood Workshops",
            "Guided Somatic Meditation & Grounding Exercises",
            "Same-Day Duty Clinician Drop-In Appointments",
        ],
        action_url="https://students.university.ac.uk/wellbeing",
        urgent_support=True,
    ),
    DepartmentCard(
        id="campus_security",
        name="Campus 24/7 Safety, Security & First Response",
        category="SECURITY",
        email="security.control@university.ac.uk",
        phone="0800 112 2334",
        office="Main Gatehouse & Security Operations Pavilion",
        hours="24 Hours / 7 Days / 365 Days a Year",
        description="24/7 rapid security dispatch, emergency medical first responders, defibrillator access, and night-time safe-walk campus escorts.",
        services=[
            "24/7 Rapid Security Dispatch & Incident Response",
            "Emergency Medical First Responders & Defibrillator Access",
            "Night-Time Campus Safe-Walk & Solo Travel Escorts",
            "Campus Safezone App Monitored SOS Alarm",
        ],
        action_url="https://students.university.ac.uk/security",
        urgent_support=True,
    ),
]


@router.get("/campus", response_model=CampusDirectoryResponse)
async def get_campus_directory(
    category: Optional[str] = Query(None, description="Filter by category (FINANCIAL, DISABILITY, HOUSING, ACADEMIC, WELLNESS, SECURITY)."),
    q: Optional[str] = Query(None, description="Search query across department name, description, and office location.", max_length=100),
) -> CampusDirectoryResponse:
    """
    Returns verified campus support departments (Financial Aid, Accommodations, Housing, Academic, Wellness, Security).
    Supports category filtering with alias resolution and full-text keyword search.
    """
    results = list(CAMPUS_DEPARTMENTS)

    # Filter by category if specified
    if category and category.strip().lower() not in ("all", "*"):
        cat_query = category.strip().lower()
        alias_map = {
            "financial": "FINANCIAL",
            "finance": "FINANCIAL",
            "aid": "FINANCIAL",
            "hardship": "FINANCIAL",
            "accommodations": "DISABILITY",
            "accommodation": "DISABILITY",
            "disability": "DISABILITY",
            "inclusion": "DISABILITY",
            "housing": "HOUSING",
            "shelter": "HOUSING",
            "residence": "HOUSING",
            "academic": "ACADEMIC",
            "appeal": "ACADEMIC",
            "su": "ACADEMIC",
            "wellness": "WELLNESS",
            "mental": "WELLNESS",
            "counseling": "WELLNESS",
            "security": "SECURITY",
            "safety": "SECURITY",
        }
        target_category = alias_map.get(cat_query, cat_query.upper())
        results = [
            d for d in results
            if d.category.upper() == target_category or target_category in d.category.upper()
        ]

    # Filter by search term
    if q and q.strip():
        query_lower = q.strip().lower()
        results = [
            d for d in results
            if query_lower in d.name.lower()
            or query_lower in d.description.lower()
            or query_lower in d.office.lower()
            or query_lower in d.category.lower()
            or any(query_lower in s.lower() for s in d.services)
        ]

    return CampusDirectoryResponse(
        status="success",
        total=len(results),
        total_count=len(results),
        departments=results,
    )
