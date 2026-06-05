"""
Leave management service for HRGenie AI.
Leave types, balances, request lifecycle (apply -> approve/reject/cancel),
holiday calendar, and overlap/balance validation.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.leave import LeaveType, LeaveBalance, LeaveRequest, LeaveApproval, Holiday, LeaveStatus
from app.models.attendance import AttendanceLog, AttendanceStatus
from app.models.employee import Employee
from app.models.auth import User


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class InsufficientBalanceError(Exception):
    pass


class OverlapError(Exception):
    pass


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class LeaveApplySchema(BaseModel):
    leave_type_id: UUID
    from_date: date
    to_date: date
    reason: str
    is_half_day: bool = False

    model_config = ConfigDict(strict=False)


class LeaveBalanceResponseSchema(BaseModel):
    leave_type_id: str
    leave_type_name: str
    total: float
    used: float
    pending: float
    available: float

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def get_leave_types(
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Get all active leave types for a company."""
    stmt = select(LeaveType).where(
        LeaveType.company_id == company_id,
        LeaveType.deleted_at.is_(None),
    ).order_by(LeaveType.name)
    result = await db.execute(stmt)
    types = result.scalars().all()

    return [
        {
            "id": str(t.id),
            "name": t.name,
            "code": t.code,
            "annual_quota": t.annual_quota,
            "carry_forward": t.carry_forward,
            "is_paid": t.is_paid,
        }
        for t in types
    ]


async def get_my_balances(
    employee_id: UUID,
    year: int,
    company_id: UUID,
    db: AsyncSession,
) -> list[LeaveBalanceResponseSchema]:
    """Get leave balances for an employee for a given year."""
    # Ensure leave balances exist for this year, if not pre-seed them from LeaveType
    types_stmt = select(LeaveType).where(
        LeaveType.company_id == company_id,
        LeaveType.deleted_at.is_(None)
    )
    types_res = await db.execute(types_stmt)
    leave_types = types_res.scalars().all()

    for lt in leave_types:
        bal_stmt = select(LeaveBalance).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == lt.id,
            LeaveBalance.year == year,
        )
        bal_res = await db.execute(bal_stmt)
        bal = bal_res.scalar_one_or_none()
        if not bal:
            bal = LeaveBalance(
                employee_id=employee_id,
                leave_type_id=lt.id,
                year=year,
                allocated=float(lt.annual_quota),
                used=0.0,
                pending=0.0,
            )
            db.add(bal)
    await db.flush()

    stmt = (
        select(LeaveBalance, LeaveType.name)
        .join(LeaveType, LeaveType.id == LeaveBalance.leave_type_id)
        .where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.year == year,
        )
        .order_by(LeaveType.name)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        LeaveBalanceResponseSchema(
            leave_type_id=str(balance.leave_type_id),
            leave_type_name=type_name,
            total=balance.allocated,
            used=balance.used,
            pending=balance.pending,
            available=balance.allocated - balance.used - balance.pending,
        )
        for balance, type_name in rows
    ]


async def apply_leave(
    employee_id: UUID,
    data: LeaveApplySchema,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """
    Apply for leave:
    - Check balance sufficient
    - Check no overlap with existing requests
    - Check not on a holiday
    - Create request pending, update balance.pending
    """
    # Calculate days
    days_count = float((data.to_date - data.from_date).days + 1)
    if data.is_half_day:
        days_count = 0.5

    # Get balance
    bal_stmt = select(LeaveBalance).where(
        LeaveBalance.employee_id == employee_id,
        LeaveBalance.leave_type_id == data.leave_type_id,
        LeaveBalance.year == data.from_date.year,
    )
    bal_result = await db.execute(bal_stmt)
    balance = bal_result.scalar_one_or_none()

    if not balance:
        raise ValueError("Leave balance not found for this leave type and year.")

    available = balance.allocated - balance.used - balance.pending
    if days_count > available:
        raise InsufficientBalanceError(
            f"Insufficient leave balance. Available: {available}, Requested: {days_count}"
        )

    # Check overlap
    overlap_stmt = select(LeaveRequest).where(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status.in_([LeaveStatus.pending, LeaveStatus.approved]),
        LeaveRequest.from_date <= data.to_date,
        LeaveRequest.to_date >= data.from_date,
        LeaveRequest.deleted_at.is_(None),
    )
    overlap_result = await db.execute(overlap_stmt)
    if overlap_result.scalar_one_or_none():
        raise OverlapError("Leave request overlaps with an existing request.")

    # Check holidays
    holiday_stmt = select(Holiday).where(
        Holiday.company_id == company_id,
        Holiday.date >= data.from_date,
        Holiday.date <= data.to_date,
    )
    holiday_result = await db.execute(holiday_stmt)
    holidays = holiday_result.scalars().all()
    if holidays:
        holiday_dates = [h.date.isoformat() for h in holidays]
        raise ValueError(
            f"Leave period includes holidays: {', '.join(holiday_dates)}. "
            "Please adjust your dates."
        )

    # Create request
    request = LeaveRequest(
        employee_id=employee_id,
        leave_type_id=data.leave_type_id,
        from_date=data.from_date,
        to_date=data.to_date,
        days_count=days_count,
        reason=data.reason,
        status=LeaveStatus.pending,
    )
    db.add(request)

    # Update pending balance
    balance.pending += days_count
    await db.flush()
    await db.refresh(request)

    return {
        "id": str(request.id),
        "from_date": request.from_date.isoformat(),
        "to_date": request.to_date.isoformat(),
        "days_count": request.days_count,
        "status": request.status.value,
        "reason": request.reason,
    }


async def get_my_leave_requests(
    employee_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Get all leave requests for an employee."""
    stmt = (
        select(LeaveRequest, LeaveType.name)
        .join(LeaveType, LeaveType.id == LeaveRequest.leave_type_id)
        .where(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.deleted_at.is_(None),
        )
        .options(selectinload(LeaveRequest.approvals).selectinload(LeaveApproval.approver))
        .order_by(LeaveRequest.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": str(req.id),
            "leave_type": type_name,
            "from_date": req.from_date.isoformat(),
            "to_date": req.to_date.isoformat(),
            "days_count": req.days_count,
            "reason": req.reason,
            "status": req.status.value,
            "approvals": [
                {
                    "approver_name": app.approver.full_name if app.approver else "System",
                    "action": app.action,
                    "comment": app.comment,
                    "actioned_at": app.actioned_at.isoformat(),
                }
                for app in req.approvals
            ],
            "created_at": req.created_at.isoformat() if req.created_at else None,
        }
        for req, type_name in rows
    ]


async def get_pending_approvals(
    approver_employee_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Get pending leave requests from reportees of this manager/approver."""
    stmt = (
        select(LeaveRequest, LeaveType.name, Employee.first_name, Employee.last_name)
        .join(LeaveType, LeaveType.id == LeaveRequest.leave_type_id)
        .join(Employee, Employee.id == LeaveRequest.employee_id)
        .where(
            Employee.company_id == company_id,
            Employee.reporting_manager_id == approver_employee_id,
            LeaveRequest.status == LeaveStatus.pending,
            LeaveRequest.deleted_at.is_(None),
        )
        .order_by(LeaveRequest.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": str(req.id),
            "employee_id": str(req.employee_id),
            "employee_name": f"{first_name} {last_name}",
            "leave_type": type_name,
            "from_date": req.from_date.isoformat(),
            "to_date": req.to_date.isoformat(),
            "days_count": req.days_count,
            "reason": req.reason,
            "status": req.status.value,
            "created_at": req.created_at.isoformat() if req.created_at else None,
        }
        for req, type_name, first_name, last_name in rows
    ]


async def approve_leave(
    request_id: UUID,
    approver_user_id: UUID,
    comment: str | None,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """
    Approve a leave request:
    - Deduct from used balance
    - Remove from pending balance
    - Mark attendance as on_leave for leave dates
    """
    stmt = (
        select(LeaveRequest)
        .join(Employee, Employee.id == LeaveRequest.employee_id)
        .where(
            LeaveRequest.id == request_id,
            Employee.company_id == company_id,
            LeaveRequest.status == LeaveStatus.pending,
            LeaveRequest.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    request = result.scalar_one_or_none()

    if not request:
        raise ValueError("Leave request not found or already processed.")

    # Update balance
    bal_stmt = select(LeaveBalance).where(
        LeaveBalance.employee_id == request.employee_id,
        LeaveBalance.leave_type_id == request.leave_type_id,
        LeaveBalance.year == request.from_date.year,
    )
    bal_result = await db.execute(bal_stmt)
    balance = bal_result.scalar_one_or_none()

    if balance:
        balance.used += request.days_count
        balance.pending = max(0.0, balance.pending - request.days_count)

    # Update request status
    request.status = LeaveStatus.approved

    # Add approval action log
    approval = LeaveApproval(
        leave_request_id=request.id,
        approver_id=approver_user_id,
        action="approved",
        comment=comment,
        actioned_at=datetime.now(timezone.utc),
    )
    db.add(approval)

    # Create attendance records as on_leave
    current_date = request.from_date
    while current_date <= request.to_date:
        if current_date.weekday() < 5:  # Skip weekends
            log_stmt = select(AttendanceLog).where(
                AttendanceLog.employee_id == request.employee_id,
                AttendanceLog.date == current_date,
                AttendanceLog.deleted_at.is_(None),
            )
            log_result = await db.execute(log_stmt)
            existing_log = log_result.scalar_one_or_none()

            if existing_log:
                existing_log.status = AttendanceStatus.on_leave
            else:
                log = AttendanceLog(
                    employee_id=request.employee_id,
                    date=current_date,
                    clock_in=datetime(current_date.year, current_date.month, current_date.day, 9, 0, tzinfo=timezone.utc),
                    clock_out=datetime(current_date.year, current_date.month, current_date.day, 18, 0, tzinfo=timezone.utc),
                    status=AttendanceStatus.on_leave,
                )
                db.add(log)

        current_date += timedelta(days=1)

    await db.flush()

    return {
        "id": str(request.id),
        "status": "approved",
    }


async def reject_leave(
    request_id: UUID,
    approver_user_id: UUID,
    comment: str | None,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Reject a leave request and restore pending balance."""
    stmt = (
        select(LeaveRequest)
        .join(Employee, Employee.id == LeaveRequest.employee_id)
        .where(
            LeaveRequest.id == request_id,
            Employee.company_id == company_id,
            LeaveRequest.status == LeaveStatus.pending,
            LeaveRequest.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    request = result.scalar_one_or_none()

    if not request:
        raise ValueError("Leave request not found or already processed.")

    # Restore pending balance
    bal_stmt = select(LeaveBalance).where(
        LeaveBalance.employee_id == request.employee_id,
        LeaveBalance.leave_type_id == request.leave_type_id,
        LeaveBalance.year == request.from_date.year,
    )
    bal_result = await db.execute(bal_stmt)
    balance = bal_result.scalar_one_or_none()

    if balance:
        balance.pending = max(0.0, balance.pending - request.days_count)

    # Reject request
    request.status = LeaveStatus.rejected

    # Log approval reject action
    approval = LeaveApproval(
        leave_request_id=request.id,
        approver_id=approver_user_id,
        action="rejected",
        comment=comment,
        actioned_at=datetime.now(timezone.utc),
    )
    db.add(approval)
    await db.flush()

    return {
        "id": str(request.id),
        "status": "rejected",
    }


async def cancel_leave(
    request_id: UUID,
    employee_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Cancel own pending leave request and restore pending balance."""
    stmt = select(LeaveRequest).where(
        LeaveRequest.id == request_id,
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status == LeaveStatus.pending,
        LeaveRequest.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    request = result.scalar_one_or_none()

    if not request:
        raise ValueError("Leave request not found or cannot be cancelled.")

    # Restore pending balance
    bal_stmt = select(LeaveBalance).where(
        LeaveBalance.employee_id == employee_id,
        LeaveBalance.leave_type_id == request.leave_type_id,
        LeaveBalance.year == request.from_date.year,
    )
    bal_result = await db.execute(bal_stmt)
    balance = bal_result.scalar_one_or_none()

    if balance:
        balance.pending = max(0.0, balance.pending - request.days_count)

    request.status = LeaveStatus.cancelled
    await db.flush()

    return {
        "id": str(request.id),
        "status": "cancelled",
    }


async def get_holidays(
    company_id: UUID,
    year: int,
    db: AsyncSession,
) -> list[dict]:
    """Get company holidays for a given year."""
    stmt = (
        select(Holiday)
        .where(
            Holiday.company_id == company_id,
            func.extract("year", Holiday.date) == year,
        )
        .order_by(Holiday.date)
    )
    result = await db.execute(stmt)
    holidays = result.scalars().all()

    return [
        {
            "id": str(h.id),
            "name": h.name,
            "date": h.date.isoformat(),
            "is_optional": h.is_optional,
        }
        for h in holidays
    ]
