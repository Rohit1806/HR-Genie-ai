"""
Leave management models: LeaveType, LeaveBalance, LeaveRequest, LeaveApproval, Holiday.
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
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LeaveStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


# ---------------------------------------------------------------------------
# LeaveType
# ---------------------------------------------------------------------------

class LeaveType(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "leave_types"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_leave_type_company_code"),
        Index("ix_leave_types_company_id", "company_id"),
    )

    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    annual_quota: Mapped[int] = mapped_column(Integer, nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    carry_forward: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


# ---------------------------------------------------------------------------
# LeaveBalance
# ---------------------------------------------------------------------------

class LeaveBalance(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "leave_balances"
    __table_args__ = (
        UniqueConstraint(
            "employee_id", "leave_type_id", "year",
            name="uq_leave_balance_employee_type_year",
        ),
        Index("ix_leave_balances_employee_id", "employee_id"),
    )

    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    leave_type_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leave_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    allocated: Mapped[float] = mapped_column(Float, nullable=False)
    used: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    pending: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    # -- relationships -------------------------------------------------------
    leave_type: Mapped["LeaveType"] = relationship(lazy="selectin")
    employee = relationship("Employee", lazy="selectin")


# ---------------------------------------------------------------------------
# LeaveRequest
# ---------------------------------------------------------------------------

class LeaveRequest(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "leave_requests"
    __table_args__ = (
        Index("ix_leave_requests_employee_id", "employee_id"),
        Index("ix_leave_requests_status", "status"),
    )

    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    leave_type_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leave_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    from_date: Mapped[date] = mapped_column(Date, nullable=False)
    to_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_count: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus, name="leave_status", create_constraint=True),
        nullable=False,
        default=LeaveStatus.pending,
    )

    # -- relationships -------------------------------------------------------
    employee = relationship("Employee", lazy="selectin")
    leave_type: Mapped["LeaveType"] = relationship(lazy="selectin")
    approvals: Mapped[list["LeaveApproval"]] = relationship(
        back_populates="leave_request", cascade="all, delete-orphan", lazy="selectin"
    )


# ---------------------------------------------------------------------------
# LeaveApproval
# ---------------------------------------------------------------------------

class LeaveApproval(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "leave_approvals"
    __table_args__ = (
        Index("ix_leave_approvals_leave_request_id", "leave_request_id"),
    )

    leave_request_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leave_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    approver_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    actioned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # -- relationships -------------------------------------------------------
    leave_request: Mapped["LeaveRequest"] = relationship(back_populates="approvals")
    approver = relationship("User", lazy="selectin")


# ---------------------------------------------------------------------------
# Holiday
# ---------------------------------------------------------------------------

class Holiday(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "holidays"
    __table_args__ = (
        UniqueConstraint("company_id", "date", name="uq_holiday_company_date"),
        Index("ix_holidays_company_id", "company_id"),
    )

    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
