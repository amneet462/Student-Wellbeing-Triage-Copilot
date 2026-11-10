"""
app/api/resource_routes.py
──────────────────────────
<<<<<<< HEAD
FastAPI routes for Campus Department Support Services Directory (Person 1).

Delivers verified institutional department cards:
  • Financial Aid & Hardship Bursary Desk
  • Accommodations, Disability & Neurodiversity Inclusion
  • Student Housing Advisory & Emergency Shelter
  • Independent Academic Regulations & Advocacy Advice

Routes non-clinical student issues directly to specialists, protecting counseling bandwidth.
=======
FastAPI routes for Campus Department Support Services Directory.
Provides comprehensive contact information, emergency phone lines,
and direct self-service referral links for non-clinical student inquiries.
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
"""

from __future__ import annotations

import logging
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resources", tags=["Campus Resources"])


class DepartmentCard(BaseModel):
<<<<<<< HEAD
    id: str = Field(..., description="Unique department identifier.")
    name: str = Field(..., description="Official university department name.")
    category: str = Field(..., description="FINANCIAL | DISABILITY | HOUSING | ACADEMIC")
    email: str = Field(..., description="Official contact email.")
    phone: str = Field(..., description="Direct helpline or desk phone.")
    office: str = Field(..., description="Physical campus building and room location.")
    hours: str = Field(..., description="Operating hours and drop-in schedule.")
    description: str = Field(..., description="Comprehensive scope of department support.")
    services: List[str] = Field(default_factory=list, description="List of primary services provided.")
    action_url: Optional[str] = Field(None, description="Direct web portal link.")


class CampusDirectoryResponse(BaseModel):
    status: str = Field("success", description="Response status.")
    total: int = Field(..., description="Number of departments returned.")
    departments: List[DepartmentCard] = Field(default_factory=list, description="List of department support cards.")


CAMPUS_DEPARTMENTS: List[DepartmentCard] = [
    DepartmentCard(
        id="financial_aid",
        name="Student Financial Hardship & Emergency Bursary Desk",
        category="FINANCIAL",
        email="student.funding@university.ac.uk",
        phone="0800 028 4455",
        office="Student Central Building, Ground Floor Suite 10",
        hours="Mon–Fri 9:00am–4:30pm",
        description="Emergency living bursaries, short-term interest-free crisis loans, digital equipment grants, and tuition fee instalment deferrals.",
        services=[
            "Emergency Non-Repayable Hardship Grants (up to £1,500)",
            "Interest-Free Short-Term Crisis Loans",
            "Tuition Fee Deferral & Payment Plan Restructuring",
            "Digital Poverty Tech Bursary (Laptops & Wi-Fi Dongles)"
        ],
        action_url="https://students.university.ac.uk/financial-aid"
    ),
    DepartmentCard(
        id="disability_services",
        name="Disability, Neurodiversity & Learning Accommodations Team",
        category="DISABILITY",
        email="disability.support@university.ac.uk",
        phone="0800 028 7788",
        office="Wilkins Building, Room 102",
        hours="Mon–Fri 8:30am–5:00pm",
        description="Reasonable exam adjustments, 25% extra time arrangements, assistive software licences, and sensory quiet room access.",
        services=[
            "Summary of Reasonable Adjustments (SoRA)",
            "25% Extra Time & Rest Breaks in Examinations",
            "Assistive Technology Software & Ergonomic Equipment",
            "Dedicated Specialist Study Skills & Mental Health Mentors"
        ],
        action_url="https://students.university.ac.uk/disability"
    ),
    DepartmentCard(
        id="emergency_housing",
        name="Student Housing Advisory & Emergency Shelter",
        category="HOUSING",
        email="housing.advice@university.ac.uk",
        phone="0800 028 9911",
        office="Campus Living Pavilion, Desk B",
        hours="24/7 Crisis Dispatch & Weekdays 9:00am–5:00pm",
        description="Immediate emergency shelter, tenancy contract disputes, guarantor schemes, and landlord dispute mediation.",
        services=[
            "Immediate Emergency Safe Shelter Placement (Same-Day)",
            "Private Tenancy Contract Review & Dispute Resolution",
            "University Rent Guarantor Scheme for International Students",
            "Deposit Protection & Housing Standard Inspections"
        ],
        action_url="https://students.university.ac.uk/housing"
    ),
    DepartmentCard(
        id="academic_advice",
        name="Student Union Independent Academic Advice & Advocacy",
        category="ACADEMIC",
        email="academic.advice@su.university.ac.uk",
        phone="0800 028 3344",
        office="Student Union Building, Floor 1",
        hours="Mon–Fri 9:30am–4:00pm",
        description="Confidential student advocacy, academic appeals, extenuating circumstances claims, disciplinary hearing representation, and course transfer guidance.",
        services=[
            "Extenuating Circumstances Policy Evidence Guidance (§4.3)",
            "Formal Academic Appeals & Grade Dispute Representation",
            "Independent Representation in Misconduct Hearings",
            "Interruption of Studies & Course Transfer Advising"
        ],
        action_url="https://su.university.ac.uk/advice"
    ),
]
=======
    id: str
    name: str
    category: str = Field(..., description="FINANCIAL | DISABILITY | HOUSING | ACADEMIC | WELLNESS | SECURITY")
    email: str
    phone: str
    office: str
    hours: str
    description: str
    action_url: Optional[str] = None
    urgent_support: bool = False


class CampusDirectoryResponse(BaseModel):
    status: str
    total_count: int
    departments: List[DepartmentCard]
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad


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
<<<<<<< HEAD
    Returns verified campus support departments (Financial Aid, Accommodations, Housing, Academic).
    Supports category filtering with alias resolution.
    """
    if not category or category.strip().lower() in ("all", "*"):
        return CampusDirectoryResponse(
            status="success",
            total=len(CAMPUS_DEPARTMENTS),
            departments=CAMPUS_DEPARTMENTS,
        )

    cat_query = category.strip().lower()
    
    # Category alias mapping
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
    }
    target_category = alias_map.get(cat_query, cat_query.upper())

    filtered = [
        d for d in CAMPUS_DEPARTMENTS
        if d.category.upper() == target_category or target_category in d.category.upper()
    ]

    return CampusDirectoryResponse(
        status="success",
        total=len(filtered),
        departments=filtered,
=======
    Returns official university support departments to route inquiries directly,
    ensuring students find financial, housing, academic, and disability aid instantly.
    """
    results = list(CAMPUS_DEPARTMENTS)

    # Filter by category
    if category:
        cat_clean = category.strip().upper()
        results = [d for d in results if d.category == cat_clean]

    # Filter by search term
    if q:
        query_lower = q.strip().lower()
        results = [
            d for d in results
            if query_lower in d.name.lower()
            or query_lower in d.description.lower()
            or query_lower in d.office.lower()
            or query_lower in d.category.lower()
        ]

    return CampusDirectoryResponse(
        status="success",
        total_count=len(results),
        departments=results,
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
    )
