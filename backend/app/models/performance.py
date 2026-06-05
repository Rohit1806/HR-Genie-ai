"""
Performance management models: PerformanceCycle, Goal, PerformanceReview, PerformanceScore.
"""

from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import (
    Date,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CycleType(str, enum.Enum):
    quarterly = "quarterly"
    half_yearly = "half_yearly"
    annual = "annual"


class CycleStatus(str, enum.Enum):
    upcoming = "upcoming"
    active = "active"
    review = "review"
    completed = "completed"


class GoalStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    deferred = "deferred"


class ReviewType(str, enum.Enum):
    self_review = "self_review"
    manager_review = "manager_review"
    peer_review = "peer_review"


# ---------------------------------------------------------------------------
# PerformanceCycle
# ---------------------------------------------------------------------------

class PerformanceCycle(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "performance_cycles"
    __table_args__ = (
        Index("ix_performance_cycles_company_id", "company_id"),
        Index("ix_performance_cycles_status", "status"),
    )

    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cycle_type: Mapped[CycleType] = mapped_column(
        Enum(CycleType, name="cycle_type", create_constraint=True),
        nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    review_start: Mapped[date] = mapped_column(Date, nullable=False)
    review_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[CycleStatus] = mapped_column(
        Enum(CycleStatus, name="cycle_status", create_constraint=True),
        nullable=False,
        default=CycleStatus.upcoming,
    )

    # -- relationships -------------------------------------------------------
    goals: Mapped[list["Goal"]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan", lazy="selectin"
    )
    reviews: Mapped[list["PerformanceReview"]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan", lazy="selectin"
    )
    scores: Mapped[list["PerformanceScore"]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan", lazy="selectin"
    )


# ---------------------------------------------------------------------------
# Goal
# ---------------------------------------------------------------------------

class Goal(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "goals"
    __table_args__ = (
        Index("ix_goals_company_id", "company_id"),
        Index("ix_goals_employee_id", "employee_id"),
        Index("ix_goals_cycle_id", "cycle_id"),
    )

    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    cycle_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("performance_cycles.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_results: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    weightage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus, name="goal_status", create_constraint=True),
        nullable=False,
        default=GoalStatus.not_started,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # -- relationships -------------------------------------------------------
    cycle: Mapped["PerformanceCycle"] = relationship(back_populates="goals")
    employee = relationship("Employee", lazy="selectin")


# ---------------------------------------------------------------------------
# PerformanceReview
# ---------------------------------------------------------------------------

class PerformanceReview(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "performance_reviews"
    __table_args__ = (
        Index("ix_performance_reviews_cycle_id", "cycle_id"),
        Index("ix_performance_reviews_employee_id", "employee_id"),
        Index("ix_performance_reviews_reviewer_id", "reviewer_id"),
    )

    cycle_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("performance_cycles.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    review_type: Mapped[ReviewType] = mapped_column(
        Enum(ReviewType, name="review_type", create_constraint=True),
        nullable=False,
    )
    ratings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # -- relationships -------------------------------------------------------
    cycle: Mapped["PerformanceCycle"] = relationship(back_populates="reviews")
    employee = relationship("Employee", lazy="selectin")
    reviewer = relationship("User", lazy="selectin")


# ---------------------------------------------------------------------------
# PerformanceScore
# ---------------------------------------------------------------------------

class PerformanceScore(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "performance_scores"
    __table_args__ = (
        UniqueConstraint("cycle_id", "employee_id", name="uq_performance_score_cycle_employee"),
        Index("ix_performance_scores_cycle_id", "cycle_id"),
        Index("ix_performance_scores_employee_id", "employee_id"),
    )

    cycle_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("performance_cycles.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    goal_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    self_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    manager_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_promotion_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_attrition_risk: Mapped[float | None] = mapped_column(Float, nullable=True)

    # -- relationships -------------------------------------------------------
    cycle: Mapped["PerformanceCycle"] = relationship(back_populates="scores")
    employee = relationship("Employee", lazy="selectin")
