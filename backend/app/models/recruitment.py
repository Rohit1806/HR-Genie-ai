"""
Recruitment models: JobPosting, Candidate, Application, AIEvaluation,
VoiceScreening, InterviewQuestions, Offer.
"""

from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class JobStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    paused = "paused"
    closed = "closed"


class ApplicationStage(str, enum.Enum):
    applied = "applied"
    ai_screening = "ai_screening"
    shortlisted = "shortlisted"
    interview = "interview"
    technical = "technical"
    hr_round = "hr_round"
    offered = "offered"
    hired = "hired"
    rejected = "rejected"


class OfferStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    expired = "expired"


# ---------------------------------------------------------------------------
# JobPosting
# ---------------------------------------------------------------------------

class JobPosting(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "job_postings"
    __table_args__ = (
        Index("ix_job_postings_company_id", "company_id"),
        Index("ix_job_postings_department_id", "department_id"),
        Index("ix_job_postings_status", "status"),
    )

    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    employment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experience_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", create_constraint=True),
        nullable=False,
        default=JobStatus.draft,
    )
    posted_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    openings_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    # -- relationships -------------------------------------------------------
    department = relationship("Department", lazy="selectin")
    poster = relationship("User", lazy="selectin")
    applications: Mapped[list["Application"]] = relationship(
        back_populates="job_posting", cascade="all, delete-orphan", lazy="selectin"
    )
    interview_questions: Mapped[list["InterviewQuestions"]] = relationship(
        back_populates="job_posting", cascade="all, delete-orphan", lazy="selectin"
    )


# ---------------------------------------------------------------------------
# Candidate
# ---------------------------------------------------------------------------

class Candidate(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint("company_id", "email", name="uq_candidate_company_email"),
        Index("ix_candidates_company_id", "company_id"),
        Index("ix_candidates_email", "email"),
    )

    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    resume_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class Application(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "job_posting_id", "candidate_id", name="uq_application_job_candidate"
        ),
        Index("ix_applications_job_posting_id", "job_posting_id"),
        Index("ix_applications_candidate_id", "candidate_id"),
        Index("ix_applications_stage", "stage"),
    )

    job_posting_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False,
    )
    candidate_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
    )
    stage: Mapped[ApplicationStage] = mapped_column(
        Enum(ApplicationStage, name="application_stage", create_constraint=True),
        nullable=False,
        default=ApplicationStage.applied,
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_ctc: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    expected_ctc: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    notice_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stage_history: Mapped[list | None] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )

    # -- relationships -------------------------------------------------------
    job_posting: Mapped["JobPosting"] = relationship(back_populates="applications")
    candidate: Mapped["Candidate"] = relationship(lazy="selectin")
    ai_evaluation: Mapped["AIEvaluation | None"] = relationship(
        back_populates="application", uselist=False, lazy="selectin"
    )
    voice_screenings: Mapped[list["VoiceScreening"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", lazy="selectin"
    )
    offer: Mapped["Offer | None"] = relationship(
        back_populates="application", uselist=False, lazy="selectin"
    )


# ---------------------------------------------------------------------------
# AIEvaluation
# ---------------------------------------------------------------------------

class AIEvaluation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_evaluations"
    __table_args__ = (
        Index("ix_ai_evaluations_application_id", "application_id", unique=True),
    )

    application_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    fit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    skill_match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strengths: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    weaknesses: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    human_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    override_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # -- relationships -------------------------------------------------------
    application: Mapped["Application"] = relationship(back_populates="ai_evaluation")


# ---------------------------------------------------------------------------
# VoiceScreening
# ---------------------------------------------------------------------------

class VoiceScreening(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "voice_screenings"
    __table_args__ = (
        Index("ix_voice_screenings_application_id", "application_id"),
    )

    application_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_evaluation: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    overall_voice_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # -- relationships -------------------------------------------------------
    application: Mapped["Application"] = relationship(back_populates="voice_screenings")


# ---------------------------------------------------------------------------
# InterviewQuestions
# ---------------------------------------------------------------------------

class InterviewQuestions(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "interview_questions"
    __table_args__ = (
        Index("ix_interview_questions_job_posting_id", "job_posting_id"),
    )

    job_posting_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False,
    )
    questions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # -- relationships -------------------------------------------------------
    job_posting: Mapped["JobPosting"] = relationship(
        back_populates="interview_questions"
    )


# ---------------------------------------------------------------------------
# Offer
# ---------------------------------------------------------------------------

class Offer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "offers"
    __table_args__ = (
        Index("ix_offers_application_id", "application_id", unique=True),
    )

    application_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    offered_salary: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    joining_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[OfferStatus] = mapped_column(
        Enum(OfferStatus, name="offer_status", create_constraint=True),
        nullable=False,
        default=OfferStatus.pending,
    )

    # -- relationships -------------------------------------------------------
    application: Mapped["Application"] = relationship(back_populates="offer")
