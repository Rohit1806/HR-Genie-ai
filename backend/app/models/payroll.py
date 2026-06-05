"""
Payroll models: SalaryStructure, EmployeeSalary, PayrollRun, PayrollEntry.
"""

from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import (
    Date,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PayrollStatus(str, enum.Enum):
    draft = "draft"
    computing = "computing"
    computed = "computed"
    approved = "approved"
    paid = "paid"


# ---------------------------------------------------------------------------
# SalaryStructure
# ---------------------------------------------------------------------------

class SalaryStructure(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "salary_structures"
    __table_args__ = (
        Index("ix_salary_structures_company_id", "company_id"),
    )

    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    components: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
        comment="Array of {name, type(earning/deduction), value, is_percentage, taxable}",
    )


# ---------------------------------------------------------------------------
# EmployeeSalary
# ---------------------------------------------------------------------------

class EmployeeSalary(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "employee_salaries"
    __table_args__ = (
        Index("ix_employee_salaries_employee_id", "employee_id"),
    )

    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    salary_structure_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("salary_structures.id", ondelete="SET NULL"),
        nullable=True,
    )
    gross_salary: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)

    # -- relationships -------------------------------------------------------
    employee = relationship("Employee", lazy="selectin")
    salary_structure: Mapped["SalaryStructure"] = relationship(lazy="selectin")


# ---------------------------------------------------------------------------
# PayrollRun
# ---------------------------------------------------------------------------

class PayrollRun(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payroll_runs"
    __table_args__ = (
        UniqueConstraint("company_id", "month", "year", name="uq_payroll_run_company_month_year"),
        Index("ix_payroll_runs_company_id", "company_id"),
    )

    company_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PayrollStatus] = mapped_column(
        Enum(PayrollStatus, name="payroll_status", create_constraint=True),
        nullable=False,
        default=PayrollStatus.draft,
    )
    total_gross: Mapped[float | None] = mapped_column(Numeric(16, 2), nullable=True)
    total_net: Mapped[float | None] = mapped_column(Numeric(16, 2), nullable=True)
    initiated_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # -- relationships -------------------------------------------------------
    entries: Mapped[list["PayrollEntry"]] = relationship(
        back_populates="payroll_run", cascade="all, delete-orphan", lazy="selectin"
    )
    initiator = relationship("User", lazy="selectin")


# ---------------------------------------------------------------------------
# PayrollEntry
# ---------------------------------------------------------------------------

class PayrollEntry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payroll_entries"
    __table_args__ = (
        Index("ix_payroll_entries_payroll_run_id", "payroll_run_id"),
        Index("ix_payroll_entries_employee_id", "employee_id"),
    )

    payroll_run_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payroll_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    gross_salary: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    basic: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    hra: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    allowances: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pf_deduction: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    esi_deduction: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    tds_deduction: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    lop_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lop_deduction: Mapped[float] = mapped_column(
        Numeric(14, 2), nullable=False, default=0
    )
    net_salary: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    # -- relationships -------------------------------------------------------
    payroll_run: Mapped["PayrollRun"] = relationship(back_populates="entries")
    employee = relationship("Employee", lazy="selectin")
