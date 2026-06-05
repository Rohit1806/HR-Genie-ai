"""
Attendance router for HRGenie AI.
Supports clock-in, clock-out, monthly attendance logs, team logs, and regularization workflows.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.auth import User, UserRole
from app.models.employee import Employee
from app.services import attendance_service
from app.schemas.attendance import (
    AttendanceLogSchema,
    AttendanceRegularizationCreateSchema,
    AttendanceRegularizationSchema,
)

router = APIRouter()


async def _get_employee(user: User, db: AsyncSession) -> Employee:
    """Helper dependency to retrieve employee from the active user session."""
    stmt = select(Employee).where(
        Employee.user_id == user.id,
        Employee.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user."
        )
    return employee


@router.post("/clock-in", response_model=dict)
async def clock_in(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Clock-in the current user's employee.
    """
    employee = await _get_employee(current_user, db)
    try:
        return await attendance_service.clock_in(
            employee_id=employee.id,
            company_id=current_user.company_id,
            db=db,
        )
    except attendance_service.AlreadyClockedInError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/clock-out", response_model=dict)
async def clock_out(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Clock-out the current user's employee.
    """
    employee = await _get_employee(current_user, db)
    try:
        return await attendance_service.clock_out(
            employee_id=employee.id,
            company_id=current_user.company_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my", response_model=dict)
async def get_my_attendance(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get monthly attendance records for the current user's employee.
    """
    employee = await _get_employee(current_user, db)
    res = await attendance_service.get_monthly_attendance(
        employee_id=employee.id,
        month=month,
        year=year,
        company_id=current_user.company_id,
        db=db,
    )
    return {
        "records": res.get("records", []),
        "summary": {
            "present_days": res.get("present_days", 0),
            "absent_days": res.get("absent_days", 0),
            "late_days": res.get("late_days", 0),
            "half_days": res.get("half_days", 0),
            "leave_days": res.get("leave_days", 0),
            "holidays": 0,
            "avg_hours": res.get("average_hours", 0.0),
            "total_working_days": res.get("total_days", 0),
        }
    }


@router.get("/team", response_model=List[dict])
async def get_team_attendance(
    date_str: str = Query(..., alias="date"),
    department_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get team attendance summary for a specific date (HR/Admin/Managers only).
    """
    if current_user.role not in (UserRole.admin, UserRole.senior_manager, UserRole.hr_recruiter):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Role not authorized to view team attendance."
        )

    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected YYYY-MM-DD."
        )

    res = await attendance_service.get_team_attendance(
        target_date=target_date,
        department_id=department_id,
        company_id=current_user.company_id,
        db=db,
    )
    return res.get("records", [])


@router.post("/regularization", response_model=dict)
async def create_regularization(
    data: AttendanceRegularizationCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit an attendance regularization request for the current user's employee.
    """
    employee = await _get_employee(current_user, db)
    try:
        return await attendance_service.create_regularization(
            employee_id=employee.id,
            date=data.date,
            requested_clock_in=data.requested_clock_in,
            requested_clock_out=data.requested_clock_out,
            reason=data.reason,
            company_id=current_user.company_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/regularization/pending", response_model=List[dict])
async def get_pending_regularizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all pending regularization requests for approval by the current user (Manager only).
    """
    employee = await _get_employee(current_user, db)
    return await attendance_service.get_pending_regularizations(
        company_id=current_user.company_id,
        approver_employee_id=employee.id,
        db=db,
    )


@router.patch("/regularization/{id}/approve", response_model=dict)
async def approve_regularization(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve an attendance regularization request.
    """
    try:
        return await attendance_service.approve_regularization(
            id=id,
            approver_id=current_user.id,
            company_id=current_user.company_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/regularization/{id}/reject", response_model=dict)
async def reject_regularization(
    id: UUID,
    body: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reject an attendance regularization request.
    """
    try:
        # Note: If reject reason is sent in body, we can capture it, though rejected logic in service simply marks it as rejected
        return await attendance_service.reject_regularization(
            id=id,
            approver_id=current_user.id,
            company_id=current_user.company_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
