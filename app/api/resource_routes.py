"""
app/api/resource_routes.py
──────────────────────────
FastAPI routes for Campus Department Support Services Directory.
Campus support services directory endpoint.
"""

from __future__ import annotations

import logging
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resources", tags=["Campus Resources"])


class DepartmentCard(BaseModel):
    id: str
    name: str
    category: str = Field(..., description="FINANCIAL | DISABILITY | HOUSING | GENERAL")
    email: str
    phone: str
    office: str
    hours: str
    description: str
    action_url: Optional[str] = None


class CampusDirectoryResponse(BaseModel):
    status: str
    departments: List[DepartmentCard]


@router.get("/campus", response_model=CampusDirectoryResponse)
async def get_campus_directory(category: Optional[str] = None) -> CampusDirectoryResponse:
    """
    Returns campus support departments (Financial Aid, Accommodations, Housing)
    to route non-clinical inquiries directly and protect counseling bandwidth.
    """
    departments = [
        DepartmentCard(
            id="financial_aid",
            name="Student Financial Hardship & Emergency Bursary Desk",
            category="FINANCIAL",
            email="student.funding@university.ac.uk",
            phone="0800 028 4455",
            office="Student Central Building, Ground Floor Suite 10",
            hours="Mon–Fri 9:00am–4:30pm",
            description="Emergency living bursaries, short-term interest-free crisis loans, and tuition fee instalment deferrals.",
            action_url="https://students.university.ac.uk/financial-aid"
        ),
        DepartmentCard(
            id="disability_services",
            name="Disability, Neurodiversity & Inclusion Team",
            category="DISABILITY",
            email="disability.support@university.ac.uk",
            phone="0800 028 7788",
            office="Wilkins Building, Room 102",
            hours="Mon–Fri 8:30am–5:00pm",
            description="Reasonable exam adjustments, extra time arrangements, assistive software licences, and sensory room access.",
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
            action_url="https://students.university.ac.uk/housing"
        ),
        DepartmentCard(
            id="academic_advice",
            name="Student Union Independent Academic Advice",
            category="ACADEMIC",
            email="academic.advice@su.university.ac.uk",
            phone="0800 028 3344",
            office="Student Union Building, Floor 1",
            hours="Mon–Fri 9:30am–4:00pm",
            description="Confidential student advocacy, academic appeals, disciplinary hearing representation, and course change guidance.",
            action_url="https://su.university.ac.uk/advice"
        )
    ]

    if category:
        filtered = [d for d in departments if d.category.lower() == category.lower()]
        return CampusDirectoryResponse(status="success", departments=filtered)

    return CampusDirectoryResponse(status="success", departments=departments)

