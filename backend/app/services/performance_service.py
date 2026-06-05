"""
Performance service for HRGenie AI.
Handles Goal planning, review cycles, and AI evaluation forecasts.
"""

from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.performance import PerformanceCycle, Goal, PerformanceReview, PerformanceScore, GoalStatus, ReviewType, CycleStatus
from app.models.employee import Employee
from app.models.auth import User


async def get_active_cycles(
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Retrieve active and review phase cycles for the company."""
    stmt = select(PerformanceCycle).where(
        PerformanceCycle.company_id == company_id,
        PerformanceCycle.status.in_([CycleStatus.active, CycleStatus.review]),
        PerformanceCycle.deleted_at.is_(None),
    ).order_by(PerformanceCycle.end_date.desc())
    result = await db.execute(stmt)
    cycles = result.scalars().all()

    return [
        {
            "id": str(c.id),
            "name": c.name,
            "cycle_type": c.cycle_type.value,
            "status": c.status.value,
            "start_date": c.start_date.isoformat(),
            "end_date": c.end_date.isoformat(),
        }
        for c in cycles
    ]


async def get_my_goals(
    employee_id: UUID,
    cycle_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Get all goals for an employee in a specific cycle."""
    stmt = select(Goal).where(
        Goal.employee_id == employee_id,
        Goal.cycle_id == cycle_id,
        Goal.deleted_at.is_(None),
    ).order_by(Goal.created_at.desc())
    result = await db.execute(stmt)
    goals = result.scalars().all()

    return [
        {
            "id": str(g.id),
            "title": g.title,
            "description": g.description,
            "key_results": g.key_results or [],
            "weightage": g.weightage,
            "status": g.status.value,
            "due_date": g.due_date.isoformat() if g.due_date else None,
        }
        for g in goals
    ]


async def create_goal(
    employee_id: UUID,
    company_id: UUID,
    data: Any,  # GoalCreateSchema
    db: AsyncSession,
) -> dict:
    """Create a new employee goal."""
    # Convert list of schemas to standard dictionaries for JSONB
    krs = [kr.model_dump() if hasattr(kr, 'model_dump') else kr for kr in data.key_results]

    goal = Goal(
        company_id=company_id,
        employee_id=employee_id,
        cycle_id=data.cycle_id,
        title=data.title,
        description=data.description,
        key_results=krs,
        weightage=data.weightage,
        status=data.status,
        due_date=data.due_date,
    )
    db.add(goal)
    await db.flush()
    await db.refresh(goal)

    return {
        "id": str(goal.id),
        "title": goal.title,
        "status": goal.status.value,
    }


async def update_goal(
    goal_id: UUID,
    employee_id: UUID,
    company_id: UUID,
    data: Any,  # GoalUpdateSchema
    db: AsyncSession,
) -> dict:
    """Update goal parameters or progress."""
    stmt = select(Goal).where(
        Goal.id == goal_id,
        Goal.employee_id == employee_id,
        Goal.company_id == company_id,
        Goal.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    goal = result.scalar_one_or_none()

    if not goal:
        raise ValueError("Goal not found.")

    if data.title is not None:
        goal.title = data.title
    if data.description is not None:
        goal.description = data.description
    if data.key_results is not None:
        krs = [kr.model_dump() if hasattr(kr, 'model_dump') else kr for kr in data.key_results]
        goal.key_results = krs
    if data.weightage is not None:
        goal.weightage = data.weightage
    if data.status is not None:
        goal.status = data.status
    if data.due_date is not None:
        goal.due_date = data.due_date

    await db.flush()
    await db.refresh(goal)

    return {
        "id": str(goal.id),
        "title": goal.title,
        "status": goal.status.value,
    }


async def submit_review(
    reviewer_user_id: UUID,
    company_id: UUID,
    data: Any,  # PerformanceReviewCreateSchema
    db: AsyncSession,
) -> dict:
    """Submit a self-review or manager review, updating score averages."""
    # Find overall score as simple average of ratings if not provided
    overall = data.overall_score
    if not overall and data.ratings:
        overall = sum(data.ratings.values()) / len(data.ratings)

    # Dynamic mock AI summary comments based on ratings
    ai_comments = []
    for k, v in data.ratings.items():
        if v >= 4.0:
            ai_comments.append(f"Outstanding performance in {k}.")
        elif v < 3.0:
            ai_comments.append(f"Needs improvement in {k}.")
    ai_summary = " ".join(ai_comments) if ai_comments else "Consistent and balanced performance across feature areas."

    review = PerformanceReview(
        cycle_id=data.cycle_id,
        employee_id=data.employee_id,
        reviewer_id=reviewer_user_id,
        review_type=data.review_type,
        ratings=data.ratings,
        feedback=data.feedback,
        overall_score=round(overall, 2) if overall else 3.0,
        ai_summary=ai_summary,
    )
    db.add(review)

    # Update PerformanceScore table totals
    score_stmt = select(PerformanceScore).where(
        PerformanceScore.cycle_id == data.cycle_id,
        PerformanceScore.employee_id == data.employee_id,
    )
    score_res = await db.execute(score_stmt)
    perf_score = score_res.scalar_one_or_none()

    if not perf_score:
        perf_score = PerformanceScore(
            cycle_id=data.cycle_id,
            employee_id=data.employee_id,
        )
        db.add(perf_score)

    # Update appropriate category score
    if data.review_type == ReviewType.self_review:
        perf_score.self_score = review.overall_score
    elif data.review_type == ReviewType.manager_review:
        perf_score.manager_score = review.overall_score

    # Compute final score
    self_s = perf_score.self_score or 3.0
    mgr_s = perf_score.manager_score or 3.0
    perf_score.final_score = round((self_s * 0.3) + (mgr_s * 0.7), 2)

    # Dynamic AI promotion and attrition forecast parameters
    perf_score.ai_promotion_score = round(min(100.0, float(perf_score.final_score) * 20.0 + 10.0), 1)
    # Attrition is inversely proportional to managers' scores
    perf_score.ai_attrition_risk = round(max(0.0, 100.0 - float(perf_score.final_score) * 20.0), 1)

    await db.flush()

    return {
        "id": str(review.id),
        "review_type": review.review_type.value,
        "overall_score": review.overall_score,
        "ai_summary": review.ai_summary,
    }


async def get_ai_insights(
    employee_id: UUID,
    cycle_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Get AI promotion score and attrition risk for an employee."""
    score_stmt = select(PerformanceScore).where(
        PerformanceScore.cycle_id == cycle_id,
        PerformanceScore.employee_id == employee_id,
    )
    score_res = await db.execute(score_stmt)
    score = score_res.scalar_one_or_none()

    if not score:
        # Fallback dynamic defaults if no cycle evaluations have occurred
        return {
            "promotion_score": 72.5,
            "attrition_risk": 15.0,
            "summary": "The employee maintains solid output and strong attendance. Moderate promotion potential in the next cycle.",
            "recommendations": [
                "Delegate technical architecture tasks to assess core design thinking.",
                "Conduct regular 1-on-1 career development discussions."
            ]
        }

    # Generate helpful text suggestions
    prom = score.ai_promotion_score or 70.0
    risk = score.ai_attrition_risk or 15.0
    
    summary = f"Employee final cycle performance score was {score.final_score or 'N/A'}. "
    if prom > 80.0:
        summary += "Highly qualified candidate displaying consistent leadership capability and technical excellence."
    else:
        summary += "Solid contributor with stable core performance metrics across targets."

    recommendations = ["Continue mentoring in specialized domains."]
    if risk > 40.0:
        recommendations.append("High attrition caution. Schedule immediate retention check-in.")
    if prom > 75.0:
        recommendations.append("Include in upcoming leadership review pipeline.")

    return {
        "promotion_score": prom,
        "attrition_risk": risk,
        "summary": summary,
        "recommendations": recommendations,
    }
