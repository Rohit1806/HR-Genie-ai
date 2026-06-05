"""
Attendance models: AttendanceLog, AttendanceRegularization.
"""

from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"
    late = "late"
    half_day = "half_day"
    on_leave = "on_leave"
    holiday = "holiday"


class RegularizationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


# ---------------------------------------------------------------------------
# AttendanceLog
# ---------------------------------------------------------------------------

class AttendanceLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "attendance_logs"
    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="uq_attendance_employee_date"),
        Index("ix_attendance_logs_employee_id", "employee_id"),
        Index("ix_attendance_logs_date", "date"),
    )

    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    clock_in: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    clock_out: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus, name="attendance_status", create_constraint=True),
        nullable=False,
    )

    # -- relationships -------------------------------------------------------
    employee = relationship("Employee", lazy="selectin")


# ---------------------------------------------------------------------------
# AttendanceRegularization
# ---------------------------------------------------------------------------

class AttendanceRegularization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "attendance_regularizations"
    __table_args__ = (
        Index("ix_attendance_regularizations_employee_id", "employee_id"),
    )

    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    requested_clock_in: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    requested_clock_out: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[RegularizationStatus] = mapped_column(
        Enum(
            RegularizationStatus,
            name="regularization_status",
            create_constraint=True,
        ),
        nullable=False,
        default=RegularizationStatus.pending,
    )
    approved_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # -- relationships -------------------------------------------------------
    employee = relationship("Employee", lazy="selectin")
    approver = relationship("User", lazy="selectin")
