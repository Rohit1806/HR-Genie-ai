"""
Attendance service for HRGenie AI.
Clock-in/out, monthly reports, team dashboards, and regularization workflow.
Late threshold: 09:30 AM.
"""

from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.attendance import AttendanceLog, AttendanceRegularization, AttendanceStatus, RegularizationStatus
from app.models.employee import Employee
from app.models.auth import User


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LATE_THRESHOLD = time(9, 30)  # 09:30 AM


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class AlreadyClockedInError(Exception):
    """Raised when employee is already clocked in."""
    pass


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def clock_in(
    employee_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """
    Clock in the employee.
    - Check not already clocked in today.
    - Determine if late (after 09:30 AM).
    """
    today = date.today()

    # Check existing record for today
    stmt = select(AttendanceLog).where(
        AttendanceLog.employee_id == employee_id,
        AttendanceLog.date == today,
        AttendanceLog.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        if not existing.clock_out:
            raise AlreadyClockedInError("Already clocked in today. Clock out first.")
        else:
            raise AlreadyClockedInError("Already completed attendance for today.")

    now = datetime.now(timezone.utc)
    # Check if late based on local time (using timezone offset or simple system local time)
    local_time = datetime.now().time()
    is_late = local_time > LATE_THRESHOLD
    status = AttendanceStatus.late if is_late else AttendanceStatus.present

    log = AttendanceLog(
        employee_id=employee_id,
        date=today,
        clock_in=now,
        status=status,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)

    return {
        "id": str(log.id),
        "date": today.isoformat(),
        "clock_in": now.isoformat(),
        "status": log.status.value,
        "is_late": is_late,
    }


async def clock_out(
    employee_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """
    Clock out the employee.
    - Find today's open log.
    - Set clock_out, compute hours, update status.
    """
    today = date.today()

    stmt = select(AttendanceLog).where(
        AttendanceLog.employee_id == employee_id,
        AttendanceLog.date == today,
        AttendanceLog.clock_out.is_(None),
        AttendanceLog.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    log = result.scalar_one_or_none()

    if not log:
        raise ValueError("No open clock-in found for today.")

    now = datetime.now(timezone.utc)
    log.clock_out = now

    # Compute hours worked
    delta = now - log.clock_in
    hours = delta.total_seconds() / 3600
    log.total_hours = round(hours, 2)

    # Determine status
    if hours < 4:
        log.status = AttendanceStatus.half_day
    elif log.clock_in.astimezone().time() > LATE_THRESHOLD:
        log.status = AttendanceStatus.late
    else:
        log.status = AttendanceStatus.present

    await db.flush()
    await db.refresh(log)

    return {
        "id": str(log.id),
        "date": today.isoformat(),
        "clock_in": log.clock_in.isoformat(),
        "clock_out": now.isoformat(),
        "total_hours": log.total_hours,
        "status": log.status.value,
    }


async def get_monthly_attendance(
    employee_id: UUID,
    month: int,
    year: int,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Get attendance summary and daily records for a specific month."""
    import calendar

    _, days_in_month = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, days_in_month)

    stmt = select(AttendanceLog).where(
        AttendanceLog.employee_id == employee_id,
        AttendanceLog.date >= start_date,
        AttendanceLog.date <= end_date,
        AttendanceLog.deleted_at.is_(None),
    ).order_by(AttendanceLog.date)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    present = sum(1 for l in logs if l.status in (AttendanceStatus.present, AttendanceStatus.late))
    late = sum(1 for l in logs if l.status == AttendanceStatus.late)
    half_days = sum(1 for l in logs if l.status == AttendanceStatus.half_day)
    on_leave = sum(1 for l in logs if l.status == AttendanceStatus.on_leave)

    total_hours = sum(l.total_hours or 0 for l in logs)
    avg_hours = total_hours / len(logs) if logs else 0

    # Business days (Mon-Fri) in month
    business_days = sum(
        1 for d in range(1, days_in_month + 1)
        if date(year, month, d).weekday() < 5
    )
    absent = business_days - present - half_days - on_leave

    records = [
        {
            "id": str(l.id),
            "date": l.date.isoformat(),
            "clock_in": l.clock_in.isoformat() if l.clock_in else None,
            "clock_out": l.clock_out.isoformat() if l.clock_out else None,
            "total_hours": l.total_hours,
            "status": l.status.value,
            "is_late": l.status == AttendanceStatus.late,
        }
        for l in logs
    ]

    return {
        "employee_id": str(employee_id),
        "month": month,
        "year": year,
        "total_days": business_days,
        "present_days": present,
        "absent_days": max(0, absent),
        "late_days": late,
        "half_days": half_days,
        "leave_days": on_leave,
        "average_hours": round(avg_hours, 2),
        "records": records,
    }


async def get_team_attendance(
    target_date: date,
    department_id: UUID | None,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Get team attendance summary for a specific date."""
    # Total active employees
    emp_q = select(func.count()).select_from(Employee).where(
        Employee.company_id == company_id,
        Employee.status == "active",
        Employee.deleted_at.is_(None),
    )
    if department_id:
        emp_q = emp_q.where(Employee.department_id == department_id)
    total_employees = (await db.execute(emp_q)).scalar() or 0

    # Attendance logs for the date
    log_q = (
        select(AttendanceLog)
        .join(Employee, Employee.id == AttendanceLog.employee_id)
        .where(
            AttendanceLog.date == target_date,
            AttendanceLog.deleted_at.is_(None),
            Employee.company_id == company_id,
            Employee.status == "active",
        )
        .options(selectinload(AttendanceLog.employee))
    )
    if department_id:
        log_q = log_q.where(Employee.department_id == department_id)

    log_result = await db.execute(log_q)
    logs = log_result.scalars().all()

    present = sum(1 for l in logs if l.status in (AttendanceStatus.present, AttendanceStatus.late))
    on_leave = sum(1 for l in logs if l.status == AttendanceStatus.on_leave)
    late = sum(1 for l in logs if l.status == AttendanceStatus.late)
    absent = total_employees - present - on_leave

    records = [
        {
            "id": str(l.id),
            "employee_id": str(l.employee_id),
            "employee_name": f"{l.employee.first_name} {l.employee.last_name}",
            "clock_in": l.clock_in.isoformat() if l.clock_in else None,
            "clock_out": l.clock_out.isoformat() if l.clock_out else None,
            "total_hours": l.total_hours,
            "status": l.status.value,
        }
        for l in logs
    ]

    return {
        "date": target_date.isoformat(),
        "total_employees": total_employees,
        "present": present,
        "absent": max(0, absent),
        "on_leave": on_leave,
        "late": late,
        "records": records,
    }


async def create_regularization(
    employee_id: UUID,
    date: date,
    requested_clock_in: datetime,
    requested_clock_out: datetime,
    reason: str,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Create a regularization request for missed or incorrect attendance."""
    # Verify employee exists
    emp_stmt = select(Employee).where(
        Employee.id == employee_id,
        Employee.company_id == company_id,
        Employee.deleted_at.is_(None),
    )
    emp_result = await db.execute(emp_stmt)
    employee = emp_result.scalar_one_or_none()
    if not employee:
        raise ValueError("Employee not found.")

    reg = AttendanceRegularization(
        employee_id=employee_id,
        date=date,
        requested_clock_in=requested_clock_in,
        requested_clock_out=requested_clock_out,
        reason=reason,
        status=RegularizationStatus.pending,
    )
    db.add(reg)
    await db.flush()
    await db.refresh(reg)

    return {
        "id": str(reg.id),
        "date": reg.date.isoformat(),
        "status": reg.status.value,
        "reason": reg.reason,
    }


async def approve_regularization(
    id: UUID,
    approver_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Approve a regularization and update/create the attendance log."""
    stmt = (
        select(AttendanceRegularization)
        .join(Employee, Employee.id == AttendanceRegularization.employee_id)
        .where(
            AttendanceRegularization.id == id,
            Employee.company_id == company_id,
            AttendanceRegularization.status == RegularizationStatus.pending,
        )
    )
    result = await db.execute(stmt)
    reg = result.scalar_one_or_none()

    if not reg:
        raise ValueError("Regularization request not found or already processed.")

    reg.status = RegularizationStatus.approved
    reg.approved_by = approver_id
    reg.updated_at = datetime.now(timezone.utc)

    # Update or create attendance log
    log_stmt = select(AttendanceLog).where(
        AttendanceLog.employee_id == reg.employee_id,
        AttendanceLog.date == reg.date,
        AttendanceLog.deleted_at.is_(None),
    )
    log_result = await db.execute(log_stmt)
    log = log_result.scalar_one_or_none()

    delta = reg.requested_clock_out - reg.requested_clock_in
    hours = round(delta.total_seconds() / 3600, 2)

    if log:
        log.clock_in = reg.requested_clock_in
        log.clock_out = reg.requested_clock_out
        log.total_hours = hours
        log.status = AttendanceStatus.present
    else:
        # Create new log
        log = AttendanceLog(
            employee_id=reg.employee_id,
            date=reg.date,
            clock_in=reg.requested_clock_in,
            clock_out=reg.requested_clock_out,
            total_hours=hours,
            status=AttendanceStatus.present,
        )
        db.add(log)

    await db.flush()

    return {
        "id": str(reg.id),
        "status": reg.status.value,
    }


async def reject_regularization(
    id: UUID,
    approver_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Reject a regularization request."""
    stmt = (
        select(AttendanceRegularization)
        .join(Employee, Employee.id == AttendanceRegularization.employee_id)
        .where(
            AttendanceRegularization.id == id,
            Employee.company_id == company_id,
            AttendanceRegularization.status == RegularizationStatus.pending,
        )
    )
    result = await db.execute(stmt)
    reg = result.scalar_one_or_none()

    if not reg:
        raise ValueError("Regularization request not found or already processed.")

    reg.status = RegularizationStatus.rejected
    reg.approved_by = approver_id
    reg.updated_at = datetime.now(timezone.utc)
    await db.flush()

    return {
        "id": str(reg.id),
        "status": reg.status.value,
    }


async def get_pending_regularizations(
    company_id: UUID,
    approver_employee_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Get all pending regularization requests for employees reporting to the manager."""
    stmt = (
        select(AttendanceRegularization)
        .join(Employee, Employee.id == AttendanceRegularization.employee_id)
        .where(
            Employee.company_id == company_id,
            Employee.reporting_manager_id == approver_employee_id,
            AttendanceRegularization.status == RegularizationStatus.pending,
        )
        .options(selectinload(AttendanceRegularization.employee))
        .order_by(AttendanceRegularization.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    return [
        {
            "id": str(reg.id),
            "employee_id": str(reg.employee_id),
            "employee_name": f"{reg.employee.first_name} {reg.employee.last_name}",
            "date": reg.date.isoformat(),
            "requested_clock_in": reg.requested_clock_in.isoformat(),
            "requested_clock_out": reg.requested_clock_out.isoformat(),
            "reason": reg.reason,
            "status": reg.status.value,
            "created_at": reg.created_at.isoformat() if reg.created_at else None,
        }
        for reg in rows
    ]
