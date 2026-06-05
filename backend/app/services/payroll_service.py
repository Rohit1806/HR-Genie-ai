"""
Payroll service for HRGenie AI.
Indian payroll with TDS new-regime computation, PF, ESI, LOP deductions.
Implements full payroll run lifecycle: initiate -> compute -> approve.
"""

import calendar
from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.payroll import SalaryStructure, EmployeeSalary, PayrollRun, PayrollEntry, PayrollStatus
from app.models.employee import Employee
from app.models.attendance import AttendanceLog, AttendanceStatus
from app.models.leave import LeaveRequest, LeaveStatus


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PayslipSchema(BaseModel):
    employee_id: str
    employee_name: str
    employee_code: str
    month: int
    year: int
    gross_salary: float
    basic: float
    hra: float
    allowances: float
    lop_days: float
    lop_deduction: float
    pf_deduction: float
    esi_deduction: float
    tds_deduction: float
    total_deductions: float
    net_salary: float

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# TDS computation — New Regime (FY 2024-25 / AY 2025-26+)
# ---------------------------------------------------------------------------

def compute_tds_new_regime(annual_gross: float) -> float:
    """
    Compute annual TDS under India's new tax regime.
    """
    standard_deduction = 75_000
    taxable = max(0.0, annual_gross - standard_deduction)

    # Section 87A rebate
    if taxable <= 700_000:
        return 0.0

    slabs = [
        (300_000, 0.00),
        (400_000, 0.05),   # 3L to 7L
        (300_000, 0.10),   # 7L to 10L
        (200_000, 0.15),   # 10L to 12L
        (300_000, 0.20),   # 12L to 15L
        (float("inf"), 0.30),  # Above 15L
    ]

    tax = 0.0
    remaining = taxable

    for slab_limit, rate in slabs:
        if remaining <= 0:
            break
        taxable_in_slab = min(remaining, slab_limit)
        tax += taxable_in_slab * rate
        remaining -= taxable_in_slab

    # Add 4% health & education cess
    tax += tax * 0.04

    return round(tax, 2)


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def initiate_payroll(
    company_id: UUID,
    month: int,
    year: int,
    user_id: UUID,
    db: AsyncSession,
) -> dict:
    """
    Initiate a payroll run for the given month/year.
    """
    dup_stmt = select(PayrollRun).where(
        PayrollRun.company_id == company_id,
        PayrollRun.month == month,
        PayrollRun.year == year,
        PayrollRun.deleted_at.is_(None),
    )
    dup_result = await db.execute(dup_stmt)
    existing = dup_result.scalar_one_or_none()
    if existing:
        raise ValueError(
            f"Payroll run already exists for {month}/{year} with status '{existing.status.value}'."
        )

    run = PayrollRun(
        company_id=company_id,
        month=month,
        year=year,
        status=PayrollStatus.draft,
        initiated_by=user_id,
    )
    db.add(run)
    await db.flush()
    await db.refresh(run)

    return {
        "id": str(run.id),
        "month": run.month,
        "year": run.year,
        "status": run.status.value,
    }


async def compute_payroll(
    run_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """
    Compute payroll entries for all active employees with salary records.
    """
    run_stmt = select(PayrollRun).where(
        PayrollRun.id == run_id,
        PayrollRun.company_id == company_id,
    )
    run_result = await db.execute(run_stmt)
    run = run_result.scalar_one_or_none()
    if not run:
        raise ValueError("Payroll run not found.")
    if run.status not in (PayrollStatus.draft, PayrollStatus.computing):
        raise ValueError(f"Payroll run is in '{run.status.value}' state, cannot compute.")

    run.status = PayrollStatus.computing
    await db.flush()

    # Month parameters
    _, days_in_month = calendar.monthrange(run.year, run.month)
    start_date = date(run.year, run.month, 1)
    end_date = date(run.year, run.month, days_in_month)

    # Business days (Mon-Fri)
    working_days = sum(
        1 for d in range(1, days_in_month + 1)
        if date(run.year, run.month, d).weekday() < 5
    )

    # Active employees with salary - get the latest salary record per employee
    emp_stmt = (
        select(Employee)
        .where(
            Employee.company_id == company_id,
            Employee.status == "active",
            Employee.deleted_at.is_(None),
        )
    )
    emp_result = await db.execute(emp_stmt)
    employees = emp_result.scalars().all()

    # Clear existing entries for this run first
    clear_stmt = select(PayrollEntry).where(PayrollEntry.payroll_run_id == run_id)
    clear_result = await db.execute(clear_stmt)
    existing_entries = clear_result.scalars().all()
    for ent in existing_entries:
        await db.delete(ent)

    total_gross = 0.0
    total_net = 0.0
    entry_count = 0

    for employee in employees:
        # Get latest salary effective
        sal_stmt = (
            select(EmployeeSalary)
            .where(
                EmployeeSalary.employee_id == employee.id,
                EmployeeSalary.effective_from <= end_date,
            )
            .order_by(desc(EmployeeSalary.effective_from))
            .limit(1)
        )
        sal_res = await db.execute(sal_stmt)
        salary = sal_res.scalar_one_or_none()
        if not salary:
            continue

        gross = float(salary.gross_salary)

        # Basic formula (approximate component splits)
        basic = gross * 0.40
        hra = basic * 0.50
        allowances = gross - basic - hra

        # Present days from attendance
        att_stmt = select(func.count()).select_from(AttendanceLog).where(
            AttendanceLog.employee_id == employee.id,
            AttendanceLog.date >= start_date,
            AttendanceLog.date <= end_date,
            AttendanceLog.status.in_([AttendanceStatus.present, AttendanceStatus.late, AttendanceStatus.half_day]),
            AttendanceLog.deleted_at.is_(None),
        )
        present_days = (await db.execute(att_stmt)).scalar() or 0

        # Approved leave days
        leave_stmt = select(func.coalesce(func.sum(LeaveRequest.days_count), 0.0)).where(
            LeaveRequest.employee_id == employee.id,
            LeaveRequest.from_date <= end_date,
            LeaveRequest.to_date >= start_date,
            LeaveRequest.status == LeaveStatus.approved,
            LeaveRequest.deleted_at.is_(None),
        )
        approved_leave_days = float((await db.execute(leave_stmt)).scalar() or 0.0)

        # LOP Days calculation
        lop_days = max(0.0, float(working_days) - float(present_days) - approved_leave_days)
        lop_deduction = (gross / working_days) * lop_days if working_days > 0 else 0.0

        # PF: 12% on min(basic, 15000)
        pf = min(basic, 15_000.0) * 0.12

        # ESI: 0.75% if gross <= 21000
        esi = gross * 0.0075 if gross <= 21_000.0 else 0.0

        # TDS: annual tax / 12
        annual_tds = compute_tds_new_regime(gross * 12.0)
        tds = annual_tds / 12.0

        # Net calculation
        total_ded = lop_deduction + pf + esi + tds
        net = max(0.0, gross - total_ded)

        entry = PayrollEntry(
            payroll_run_id=run.id,
            employee_id=employee.id,
            gross_salary=gross,
            basic=round(basic, 2),
            hra=round(hra, 2),
            allowances={"allowances": round(allowances, 2)},
            pf_deduction=round(pf, 2),
            esi_deduction=round(esi, 2),
            tds_deduction=round(tds, 2),
            lop_days=int(lop_days),
            lop_deduction=round(lop_deduction, 2),
            net_salary=round(net, 2),
        )
        db.add(entry)

        total_gross += gross
        total_net += net
        entry_count += 1

    # Update run totals
    run.total_gross = round(total_gross, 2)
    run.total_net = round(total_net, 2)
    run.status = PayrollStatus.computed

    await db.flush()
    await db.refresh(run)

    return {
        "id": str(run.id),
        "status": run.status.value,
        "total_employees": entry_count,
        "total_gross": float(run.total_gross) if run.total_gross else 0.0,
        "total_net": float(run.total_net) if run.total_net else 0.0,
    }


async def get_payroll_runs(
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Get all payroll runs for a company."""
    stmt = (
        select(PayrollRun)
        .where(
            PayrollRun.company_id == company_id,
            PayrollRun.deleted_at.is_(None),
        )
        .order_by(PayrollRun.year.desc(), PayrollRun.month.desc())
    )
    result = await db.execute(stmt)
    runs = result.scalars().all()

    return [
        {
            "id": str(r.id),
            "month": r.month,
            "year": r.year,
            "status": r.status.value,
            "total_gross": float(r.total_gross) if r.total_gross else 0.0,
            "total_net": float(r.total_net) if r.total_net else 0.0,
            "initiated_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in runs
    ]


async def get_payroll_entries(
    run_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Get all payroll entries for a specific run."""
    stmt = (
        select(PayrollEntry)
        .join(Employee, Employee.id == PayrollEntry.employee_id)
        .where(
            PayrollEntry.payroll_run_id == run_id,
            Employee.company_id == company_id,
        )
        .options(selectinload(PayrollEntry.employee))
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()

    return [
        {
            "id": str(e.id),
            "employee_id": str(e.employee_id),
            "employee_code": e.employee.employee_code,
            "employee_name": f"{e.employee.first_name} {e.employee.last_name}",
            "gross_salary": float(e.gross_salary),
            "basic": float(e.basic),
            "hra": float(e.hra),
            "allowances": e.allowances.get("allowances", 0.0) if e.allowances else 0.0,
            "lop_days": e.lop_days,
            "lop_deduction": float(e.lop_deduction),
            "pf_deduction": float(e.pf_deduction),
            "esi_deduction": float(e.esi_deduction),
            "tds_deduction": float(e.tds_deduction),
            "net_salary": float(e.net_salary),
        }
        for e in entries
    ]


async def approve_payroll(
    run_id: UUID,
    company_id: UUID,
    approver_id: UUID,
    db: AsyncSession,
) -> dict:
    """Approve a computed payroll run."""
    stmt = select(PayrollRun).where(
        PayrollRun.id == run_id,
        PayrollRun.company_id == company_id,
    )
    result = await db.execute(stmt)
    run = result.scalar_one_or_none()

    if not run:
        raise ValueError("Payroll run not found.")
    if run.status != PayrollStatus.computed:
        raise ValueError(f"Cannot approve a payroll run in '{run.status.value}' status.")

    run.status = PayrollStatus.approved
    await db.flush()

    return {
        "id": str(run.id),
        "status": run.status.value,
    }


async def get_payslip(
    employee_id: UUID,
    month: int,
    year: int,
    company_id: UUID,
    db: AsyncSession,
) -> PayslipSchema | None:
    """Get payslip for an employee for a specific month."""
    stmt = (
        select(PayrollEntry)
        .join(PayrollRun, PayrollRun.id == PayrollEntry.payroll_run_id)
        .join(Employee, Employee.id == PayrollEntry.employee_id)
        .where(
            PayrollEntry.employee_id == employee_id,
            Employee.company_id == company_id,
            PayrollRun.month == month,
            PayrollRun.year == year,
            PayrollRun.status == PayrollStatus.approved,
        )
        .options(selectinload(PayrollEntry.employee))
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()

    if not entry:
        return None

    # Calculate values
    allowance_val = entry.allowances.get("allowances", 0.0) if entry.allowances else 0.0
    total_ded = entry.lop_deduction + entry.pf_deduction + entry.esi_deduction + entry.tds_deduction

    return PayslipSchema(
        employee_id=str(entry.employee_id),
        employee_name=f"{entry.employee.first_name} {entry.employee.last_name}",
        employee_code=entry.employee.employee_code,
        month=month,
        year=year,
        gross_salary=float(entry.gross_salary),
        basic=float(entry.basic),
        hra=float(entry.hra),
        allowances=float(allowance_val),
        lop_days=float(entry.lop_days),
        lop_deduction=float(entry.lop_deduction),
        pf_deduction=float(entry.pf_deduction),
        esi_deduction=float(entry.esi_deduction),
        tds_deduction=float(entry.tds_deduction),
        total_deductions=float(total_ded),
        net_salary=float(entry.net_salary),
    )
