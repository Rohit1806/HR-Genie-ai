"""
Leave management API router for HRGenie AI.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.auth import User
from app.models.employee import Employee
from app.services import leave_service
from app.schemas.leave import LeaveRequestCreateSchema

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


@router.get("/types", response_model=List[dict])
async def get_leave_types(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active leave types.
    """
    return await leave_service.get_leave_types(
        company_id=current_user.company_id,
        db=db,
    )


@router.get("/my-balances", response_model=List[dict])
async def get_my_balances(
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get leave balances of the current logged-in employee.
    """
    employee = await _get_employee(current_user, db)
    target_year = year or date.today().year
    return await leave_service.get_my_balances(
        employee_id=employee.id,
        year=target_year,
        company_id=current_user.company_id,
        db=db,
    )


@router.post("/apply", response_model=dict)
async def apply_leave(
    data: LeaveRequestCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Apply for leave request.
    """
    employee = await _get_employee(current_user, db)
    try:
        # Wrap the schema in the service model
        srv_data = leave_service.LeaveApplySchema(
            leave_type_id=data.leave_type_id,
            from_date=data.from_date,
            to_date=data.to_date,
            reason=data.reason,
            is_half_day=False,
        )
        return await leave_service.apply_leave(
            employee_id=employee.id,
            data=srv_data,
            company_id=current_user.company_id,
            db=db,
        )
    except (leave_service.InsufficientBalanceError, leave_service.OverlapError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my-requests", response_model=dict)
async def get_my_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all leave requests submitted by the current employee (paginated wrapper).
    """
    employee = await _get_employee(current_user, db)
    requests = await leave_service.get_my_leave_requests(
        employee_id=employee.id,
        company_id=current_user.company_id,
        db=db,
    )
    # Simple pagination wrapper for UI
    total = len(requests)
    offset = (page - 1) * page_size
    items = requests[offset:offset + page_size]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }


@router.get("/pending-approvals", response_model=dict)
async def get_pending_approvals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get pending leave requests from reportees of this manager (paginated wrapper).
    """
    employee = await _get_employee(current_user, db)
    requests = await leave_service.get_pending_approvals(
        approver_employee_id=employee.id,
        company_id=current_user.company_id,
        db=db,
    )
    # Simple pagination wrapper for UI
    total = len(requests)
    offset = (page - 1) * page_size
    items = requests[offset:offset + page_size]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }


@router.patch("/{id}/approve", response_model=dict)
async def approve_leave(
    id: UUID,
    body: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve a pending leave request.
    """
    comment = body.get("remarks") if body else None
    try:
        return await leave_service.approve_leave(
            request_id=id,
            approver_user_id=current_user.id,
            comment=comment,
            company_id=current_user.company_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{id}/reject", response_model=dict)
async def reject_leave(
    id: UUID,
    body: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reject a pending leave request.
    """
    comment = body.get("reason") if body else None
    try:
        return await leave_service.reject_leave(
            request_id=id,
            approver_user_id=current_user.id,
            comment=comment,
            company_id=current_user.company_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{id}/cancel", response_model=dict)
async def cancel_leave(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel an own pending leave request.
    """
    employee = await _get_employee(current_user, db)
    try:
        return await leave_service.cancel_leave(
            request_id=id,
            employee_id=employee.id,
            company_id=current_user.company_id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/holidays", response_model=List[dict])
async def get_holidays(
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get company holidays for a given year.
    """
    target_year = year or date.today().year
    return await leave_service.get_holidays(
        company_id=current_user.company_id,
        year=target_year,
        db=db,
    )
