"""
Performance management API router for HRGenie AI.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.auth import User, UserRole
from app.models.employee import Employee
from app.services import performance_service
from app.schemas.performance import (
    GoalCreateSchema,
    GoalUpdateSchema,
    PerformanceReviewCreateSchema,
    PerformanceCycleSchema,
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


@router.get("/cycles", response_model=dict)
async def list_performance_cycles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List active or upcoming performance cycles.
    """
    cycles = await performance_service.get_active_cycles(
        company_id=current_user.company_id,
        db=db,
    )
    total = len(cycles)
    offset = (page - 1) * page_size
    items = cycles[offset:offset + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }


@router.post("/cycles", response_model=dict)
async def create_performance_cycle(
    data: dict,  # Freeform cycle creation or schema
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new performance cycle (HR/Admin only).
    """
    if current_user.role not in (UserRole.ADMIN, UserRole.HR_RECRUITER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )
    from app.models.performance import PerformanceCycle, CycleType, CycleStatus
    now = datetime.now(timezone.utc) if hasattr(datetime, "now") else datetime.utcnow()
    cycle = PerformanceCycle(
        company_id=current_user.company_id,
        name=data.get("name", "Performance Cycle"),
        cycle_type=CycleType(data.get("cycle_type", "quarterly")),
        start_date=date.fromisoformat(data.get("start_date")),
        end_date=date.fromisoformat(data.get("end_date")),
        review_start=date.fromisoformat(data.get("review_start")),
        review_end=date.fromisoformat(data.get("review_end")),
        status=CycleStatus.active,
    )
    db.add(cycle)
    await db.flush()
    await db.refresh(cycle)

    return {
        "id": str(cycle.id),
        "name": cycle.name,
        "status": cycle.status.value,
    }


@router.get("/goals", response_model=List[dict])
async def get_my_goals(
    cycle_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all goals for the logged-in employee for the given performance cycle.
    """
    employee = await _get_employee(current_user, db)
    return await performance_service.get_my_goals(
        employee_id=employee.id,
        cycle_id=cycle_id,
        db=db,
    )


@router.post("/goals", response_model=dict)
async def create_goal(
    data: GoalCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new goal for the logged-in employee.
    """
    employee = await _get_employee(current_user, db)
    return await performance_service.create_goal(
        employee_id=employee.id,
        company_id=current_user.company_id,
        data=data,
        db=db,
    )


@router.patch("/goals/{id}", response_model=dict)
async def update_goal(
    id: UUID,
    data: GoalUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update details, status, or key results progress of a goal.
    """
    employee = await _get_employee(current_user, db)
    try:
        return await performance_service.update_goal(
            goal_id=id,
            employee_id=employee.id,
            company_id=current_user.company_id,
            data=data,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/reviews/self", response_model=dict)
async def submit_self_review(
    data: dict,  # SelfReviewData structure from UI
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a self-evaluation performance review.
    """
    employee = await _get_employee(current_user, db)
    try:
        srv_data = PerformanceReviewCreateSchema(
            cycle_id=UUID(data.get("cycle_id")),
            employee_id=employee.id,
            review_type="self_review",
            ratings=data.get("ratings", {}),
            feedback=data.get("feedback", ""),
        )
        return await performance_service.submit_review(
            reviewer_user_id=current_user.id,
            company_id=current_user.company_id,
            data=srv_data,
            db=db,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reviews/manager", response_model=dict)
async def submit_manager_review(
    data: dict,  # ManagerReviewData structure from UI
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a manager's performance evaluation for an employee.
    """
    if current_user.role not in (UserRole.ADMIN, UserRole.SENIOR_MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Managers only can submit team evaluations."
        )

    try:
        srv_data = PerformanceReviewCreateSchema(
            cycle_id=UUID(data.get("cycle_id")),
            employee_id=UUID(data.get("employee_id")),
            review_type="manager_review",
            ratings=data.get("ratings", {}),
            feedback=data.get("feedback", ""),
            overall_score=data.get("overall_score"),
        )
        return await performance_service.submit_review(
            reviewer_user_id=current_user.id,
            company_id=current_user.company_id,
            data=srv_data,
            db=db,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/scores", response_model=List[dict])
async def get_performance_scores(
    cycle_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get performance scores summaries (for HR/Managers or individual).
    """
    # Simple query to list summaries in the system
    from app.models.performance import PerformanceScore
    stmt = select(PerformanceScore).where(
        PerformanceScore.deleted_at.is_(None) if hasattr(PerformanceScore, 'deleted_at') else True
    )
    if cycle_id:
        stmt = stmt.where(PerformanceScore.cycle_id == cycle_id)

    res = await db.execute(stmt)
    scores = res.scalars().all()

    return [
        {
            "id": str(s.id),
            "cycle_id": str(s.cycle_id),
            "employee_id": str(s.employee_id),
            "goal_score": s.goal_score,
            "self_score": s.self_score,
            "manager_score": s.manager_score,
            "final_score": s.final_score,
            "ai_promotion_score": s.ai_promotion_score,
            "ai_attrition_risk": s.ai_attrition_risk,
        }
        for s in scores
    ]


@router.get("/insights", response_model=dict)
async def get_ai_insights(
    cycle_id: UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI evaluation insights and career promotion forecasts for the current employee.
    """
    employee = await _get_employee(current_user, db)
    return await performance_service.get_ai_insights(
        employee_id=employee.id,
        cycle_id=cycle_id,
        company_id=current_user.company_id,
        db=db,
    )
