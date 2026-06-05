"""
Employee Pydantic v2 schemas.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


# ---------------------------------------------------------------------------
# Skill & Document sub-schemas
# ---------------------------------------------------------------------------

class SkillSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    name: str
    category: str | None = None
    proficiency: str | None = None
    years_experience: float | None = None


class DocumentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_type: str
    file_name: str
    file_url: str
    file_size_bytes: int
    created_at: datetime


class HistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: str
    previous_value: dict | None = None
    new_value: dict | None = None
    effective_date: date
    reason: str | None = None


# ---------------------------------------------------------------------------
# Create / Update
# ---------------------------------------------------------------------------

class EmployeeCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    phone: str
    personal_email: EmailStr
    address: dict | None = None
    emergency_contact: dict | None = None
    date_of_joining: date
    employment_type: str
    department_id: UUID
    designation_id: UUID
    reporting_manager_id: UUID | None = None
    work_location: str | None = None


class EmployeeUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    personal_email: EmailStr | None = None
    address: dict | None = None
    emergency_contact: dict | None = None
    date_of_joining: date | None = None
    employment_type: str | None = None
    department_id: UUID | None = None
    designation_id: UUID | None = None
    reporting_manager_id: UUID | None = None
    work_location: str | None = None
    employment_status: str | None = None
    profile_photo_url: str | None = None


# ---------------------------------------------------------------------------
# Read (Summary / Detail)
# ---------------------------------------------------------------------------

class EmployeeSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_code: str
    full_name: str
    department_name: str | None = None
    designation_title: str | None = None
    employment_status: str
    profile_photo_url: str | None = None
    date_of_joining: date


class EmployeeDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_code: str
    full_name: str
    department_name: str | None = None
    designation_title: str | None = None
    employment_status: str
    profile_photo_url: str | None = None
    date_of_joining: date
    personal_email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    address: dict | None = None
    emergency_contact: dict | None = None
    reporting_manager_name: str | None = None
    skills: list[SkillSchema] = []
    documents: list[DocumentSchema] = []
    history: list[HistorySchema] = []


# ---------------------------------------------------------------------------
# List response (paginated)
# ---------------------------------------------------------------------------

class EmployeeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[EmployeeSummarySchema]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------------------
# Org chart
# ---------------------------------------------------------------------------

class OrgChartNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    designation: str
    department: str
    photo_url: str | None = None
    children: list["OrgChartNode"] = []
