"""
Recruitment Pydantic v2 schemas.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


# ---------------------------------------------------------------------------
# AIEvaluation
# ---------------------------------------------------------------------------

class AIEvaluationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    fit_score: float | None = None
    skill_match_score: float | None = None
    experience_score: float | None = None
    overall_score: float | None = None
    strengths: list | None = None
    weaknesses: list | None = None
    ai_summary: str | None = None
    recommendation: str | None = None
    confidence: float | None = None
    human_override: bool = False
    override_notes: str | None = None


# ---------------------------------------------------------------------------
# Job Posting
# ---------------------------------------------------------------------------

class JobPostingCreateSchema(BaseModel):
    title: str
    department_id: UUID | None = None
    employment_type: str
    location: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    description: str
    requirements: str | None = None
    experience_min: int | None = None
    experience_max: int | None = None
    openings_count: int = 1
    deadline: date | None = None


class JobPostingUpdateSchema(BaseModel):
    title: Optional[str] = None
    department_id: Optional[UUID] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    status: Optional[str] = None
    openings_count: Optional[int] = None
    deadline: Optional[date] = None


class JobPostingSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    department_name: str | None = None
    employment_type: str
    location: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    status: str
    openings_count: int
    applications_count: int = 0
    created_at: datetime


class JobPostingDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    department_id: UUID | None = None
    department_name: str | None = None
    employment_type: str
    location: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    description: str
    requirements: str | None = None
    experience_min: int | None = None
    experience_max: int | None = None
    status: str
    openings_count: int
    deadline: date | None = None
    posted_by_name: str | None = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Candidate
# ---------------------------------------------------------------------------

class CandidateCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    linkedin_url: str | None = None
    resume_url: str | None = None


class CandidateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    linkedin_url: str | None = None
    resume_url: str | None = None


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class ApplicationCreateSchema(BaseModel):
    job_posting_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    linkedin_url: str | None = None
    source: str | None = None
    current_ctc: float | None = None
    expected_ctc: float | None = None
    notice_period_days: int | None = None


class ApplicationStageUpdateSchema(BaseModel):
    stage: str
    rejection_reason: str | None = None


class ApplicationSummarySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_posting_id: UUID
    job_title: str
    candidate_id: UUID
    candidate_name: str
    stage: str
    applied_at: datetime
    overall_score: float | None = None
    recommendation: str | None = None


class ApplicationDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_posting_id: UUID
    job_title: str
    candidate: CandidateSchema
    stage: str
    applied_at: datetime
    source: str | None = None
    rejection_reason: str | None = None
    current_ctc: float | None = None
    expected_ctc: float | None = None
    notice_period_days: int | None = None
    stage_history: list = []
    ai_evaluation: AIEvaluationSchema | None = None


# ---------------------------------------------------------------------------
# Offer
# ---------------------------------------------------------------------------

class OfferCreateSchema(BaseModel):
    application_id: UUID
    offered_salary: float
    joining_date: date


class OfferSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    offered_salary: float
    joining_date: date
    status: str
    created_at: datetime
