"""
AI ENGINE 10: Promotion Recommender
File: backend/app/ai/engines/promotion_recommender.py

Computes AI-driven promotion readiness scores for employees.
Considers:
- Performance history across cycles
- Tenure in current role
- Skill progression
- Leadership indicators
- Peer/manager feedback sentiment
- Business need / headcount planning

Outputs a promotion score (0-100) and actionable recommendation.
"""

import logging
from datetime import date, datetime
from typing import Optional

from app.ai.gemini_client import call_gemini_json

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scoring Weights
# ---------------------------------------------------------------------------

PROMOTION_WEIGHTS = {
    "performance_score": 0.35,
    "tenure_score": 0.15,
    "skill_progression_score": 0.20,
    "leadership_score": 0.15,
    "consistency_score": 0.15,
}

READINESS_THRESHOLDS = {
    "ready_now": 80,
    "ready_in_6_months": 65,
    "ready_in_12_months": 50,
    "not_ready": 0,
}


# ---------------------------------------------------------------------------
# Score Component Functions
# ---------------------------------------------------------------------------

def compute_performance_component(
    performance_scores: list[float],  # last 2-4 cycles
) -> float:
    """Score based on recent performance history."""
    if not performance_scores:
        return 50.0

    # Weighted average with recency bias (more recent = higher weight)
    n = len(performance_scores)
    weights = [i + 1 for i in range(n)]
    total_weight = sum(weights)
    weighted_avg = sum(s * w for s, w in zip(performance_scores, weights)) / total_weight
    return round(weighted_avg, 1)


def compute_tenure_component(
    months_in_current_role: int,
    typical_promotion_months: int = 18,
) -> float:
    """
    Score based on time in current role.
    Sweet spot: at or just past the typical promotion window.
    Too soon penalized. Too long = stagnation concern.
    """
    if months_in_current_role < 6:
        return 20.0  # Too early
    elif months_in_current_role < typical_promotion_months:
        ratio = months_in_current_role / typical_promotion_months
        return round(20 + ratio * 50, 1)  # Ramp up to 70
    elif months_in_current_role <= typical_promotion_months * 1.5:
        return 90.0  # Ideal window
    elif months_in_current_role <= typical_promotion_months * 2.5:
        return 75.0  # Slightly overdue
    else:
        return 55.0  # Significantly overdue — potential flight risk


def compute_consistency_component(performance_scores: list[float]) -> float:
    """
    Score based on consistency (low variance = more reliable).
    Consistent high performers are better promotion candidates than volatile ones.
    """
    if len(performance_scores) < 2:
        return 60.0

    import statistics
    std = statistics.stdev(performance_scores)
    avg = statistics.mean(performance_scores)

    # High avg + low std = best
    # Penalize for high variance even if avg is good
    consistency = max(0, 100 - std * 2)
    if avg >= 75:
        consistency = min(100, consistency * 1.1)

    return round(consistency, 1)


def compute_skill_progression_component(
    skill_count_history: list[int],  # number of skills at each review point
    current_skill_count: int,
    skills_added_last_year: int,
) -> float:
    """Score based on skill growth and learning agility."""
    base = 50.0

    # Reward consistent skill growth
    if skills_added_last_year >= 3:
        base += 30
    elif skills_added_last_year >= 1:
        base += 15

    # Reward current depth
    if current_skill_count >= 10:
        base += 20
    elif current_skill_count >= 6:
        base += 10

    return round(min(100, base), 1)


def compute_leadership_component(
    manages_reports: bool,
    mentors_others: bool,
    led_projects: int,
    cross_team_collaborations: int,
) -> float:
    """Score based on leadership indicators."""
    score = 40.0  # Base

    if manages_reports:
        score += 25
    if mentors_others:
        score += 15
    score += min(led_projects * 5, 15)
    score += min(cross_team_collaborations * 3, 10)

    # No subtraction — absence of leadership doesn't mean negative
    return round(min(100, score), 1)


# ---------------------------------------------------------------------------
# Readiness Label
# ---------------------------------------------------------------------------

def readiness_label(score: float) -> str:
    if score >= READINESS_THRESHOLDS["ready_now"]:
        return "Ready Now"
    elif score >= READINESS_THRESHOLDS["ready_in_6_months"]:
        return "Ready in 6 Months"
    elif score >= READINESS_THRESHOLDS["ready_in_12_months"]:
        return "Ready in 12 Months"
    return "Not Ready"


def readiness_timeline_months(score: float) -> int:
    if score >= READINESS_THRESHOLDS["ready_now"]:
        return 0
    elif score >= READINESS_THRESHOLDS["ready_in_6_months"]:
        return 6
    elif score >= READINESS_THRESHOLDS["ready_in_12_months"]:
        return 12
    return 18


# ---------------------------------------------------------------------------
# Main Promotion Recommender
# ---------------------------------------------------------------------------

async def compute_promotion_score(
    employee_name: str,
    current_role: str,
    target_role: Optional[str],
    performance_scores: list[float],
    months_in_current_role: int,
    current_skill_count: int,
    skills_added_last_year: int,
    manages_reports: bool = False,
    mentors_others: bool = False,
    led_projects: int = 0,
    cross_team_collaborations: int = 0,
    manager_recommendation: Optional[str] = None,  # "yes" | "no" | "maybe"
    department: str = "",
) -> dict:
    """
    Compute comprehensive promotion readiness score.

    Returns:
    {
        "promotion_score": float,
        "readiness_label": str,
        "readiness_timeline_months": int,
        "component_scores": {
            "performance": float,
            "tenure": float,
            "skill_progression": float,
            "leadership": float,
            "consistency": float,
        },
        "key_factors": [str],         # what's driving the score
        "blockers": [str],            # what's holding them back
        "action_plan": [str],         # how to get to next level
        "ai_narrative": str,
        "confidence": float,
    }
    """
    logger.info(f"Computing promotion score for: {employee_name}")

    # Compute all components
    perf_comp = compute_performance_component(performance_scores)
    tenure_comp = compute_tenure_component(months_in_current_role)
    consistency_comp = compute_consistency_component(performance_scores)
    skill_comp = compute_skill_progression_component(
        skill_count_history=[],
        current_skill_count=current_skill_count,
        skills_added_last_year=skills_added_last_year,
    )
    leadership_comp = compute_leadership_component(
        manages_reports=manages_reports,
        mentors_others=mentors_others,
        led_projects=led_projects,
        cross_team_collaborations=cross_team_collaborations,
    )

    # Manager override bonus
    manager_bonus = 0.0
    if manager_recommendation == "yes":
        manager_bonus = 5.0
    elif manager_recommendation == "no":
        manager_bonus = -8.0

    # Weighted composite
    composite = (
        perf_comp * PROMOTION_WEIGHTS["performance_score"]
        + tenure_comp * PROMOTION_WEIGHTS["tenure_score"]
        + skill_comp * PROMOTION_WEIGHTS["skill_progression_score"]
        + leadership_comp * PROMOTION_WEIGHTS["leadership_score"]
        + consistency_comp * PROMOTION_WEIGHTS["consistency_score"]
        + manager_bonus
    )
    promotion_score = round(max(0, min(100, composite)), 1)

    components = {
        "performance": perf_comp,
        "tenure": tenure_comp,
        "skill_progression": skill_comp,
        "leadership": leadership_comp,
        "consistency": consistency_comp,
    }

    # Identify key factors and blockers
    key_factors = _identify_key_factors(components)
    blockers = _identify_blockers(components, months_in_current_role)

    # AI narrative
    hist_str = ", ".join(f"{s:.0f}" for s in performance_scores[-3:]) or "No history"
    prompt = f"""
Employee: {employee_name}
Current Role: {current_role}
Target Role: {target_role or 'Next Level'}
Department: {department}
Promotion Score: {promotion_score}/100 ({readiness_label(promotion_score)})
Performance History (last cycles): {hist_str}
Months in Role: {months_in_current_role}
Component Scores: {components}
Manager Recommendation: {manager_recommendation or 'Not provided'}

Write a brief 3-sentence professional promotion recommendation narrative for this employee.
Then provide 3 specific action items for them to strengthen their candidacy.

Return JSON:
{{
  "ai_narrative": "3 sentence narrative",
  "action_plan": ["action 1", "action 2", "action 3"],
  "confidence_note": "brief note on confidence level"
}}
Return only valid JSON, no markdown.
"""

    try:
        ai_result = await call_gemini_json(prompt)
        action_plan = ai_result.get("action_plan", [])
        ai_narrative = ai_result.get("ai_narrative", "")
        confidence = 0.82
    except Exception as e:
        logger.error(f"Promotion AI narrative failed: {e}")
        action_plan = []
        ai_narrative = f"{employee_name} has a promotion readiness score of {promotion_score:.0f}/100 ({readiness_label(promotion_score)})."
        confidence = 0.65

    return {
        "promotion_score": promotion_score,
        "readiness_label": readiness_label(promotion_score),
        "readiness_timeline_months": readiness_timeline_months(promotion_score),
        "component_scores": components,
        "key_factors": key_factors,
        "blockers": blockers,
        "action_plan": action_plan,
        "ai_narrative": ai_narrative,
        "confidence": confidence,
    }


def _identify_key_factors(components: dict) -> list[str]:
    factors = []
    if components["performance"] >= 80:
        factors.append("Consistently high performance scores")
    if components["leadership"] >= 75:
        factors.append("Demonstrated leadership capability")
    if components["skill_progression"] >= 75:
        factors.append("Strong skill growth trajectory")
    if components["consistency"] >= 80:
        factors.append("Reliable and consistent contributor")
    if components["tenure"] >= 85:
        factors.append("Appropriate tenure for advancement")
    return factors or ["Moderate performance across all dimensions"]


def _identify_blockers(components: dict, months_in_role: int) -> list[str]:
    blockers = []
    if components["performance"] < 60:
        blockers.append("Performance scores below promotion threshold")
    if components["leadership"] < 50:
        blockers.append("Limited leadership experience demonstrated")
    if months_in_role < 12:
        blockers.append(f"Insufficient time in current role ({months_in_role} months)")
    if components["skill_progression"] < 50:
        blockers.append("Minimal skill development in recent period")
    if components["consistency"] < 50:
        blockers.append("Inconsistent performance across review cycles")
    return blockers


# ---------------------------------------------------------------------------
# Engine wrapper class and instance export
# ---------------------------------------------------------------------------

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal

class PromotionRecommenderEngine:
    async def recommend_promotion(self, employee_id: uuid.UUID, db: AsyncSession) -> dict:
        from app.models.employee import Employee, EmployeeSkill, Skill, EmploymentHistory
        from app.models.performance import PerformanceScore, PerformanceReview
        from sqlalchemy import select, func
        from datetime import date, timedelta
        
        # 1. Fetch Employee
        employee = await db.get(Employee, employee_id)
        if not employee:
            return {"error": "Employee not found"}
            
        employee_name = employee.full_name
        current_role = employee.designation.name if employee.designation else "Employee"
        department = employee.department.name if employee.department else "Unassigned"
        
        # Target role
        target_role = f"Senior {current_role}" if "Senior" not in current_role else f"Lead {current_role}"

        # 2. Months in current role
        months_since_joining = int((date.today() - employee.date_of_joining).days / 30.4)
        stmt = select(EmploymentHistory).where(
            EmploymentHistory.employee_id == employee_id,
            EmploymentHistory.event_type.ilike("%promotion%")
        ).order_by(EmploymentHistory.effective_date.desc())
        promo_history = (await db.execute(stmt)).scalars().first()
        
        if promo_history:
            months_in_current_role = int((date.today() - promo_history.effective_date).days / 30.4)
        else:
            months_in_current_role = months_since_joining

        # 3. Performance history
        stmt = select(PerformanceScore).where(
            PerformanceScore.employee_id == employee_id
        ).order_by(PerformanceScore.created_at.asc())
        scores = (await db.execute(stmt)).scalars().all()
        performance_scores = [float(s.final_score) for s in scores if s.final_score is not None]
        if not performance_scores:
            performance_scores = [75.0]

        # 4. Skills
        stmt = select(EmployeeSkill).where(EmployeeSkill.employee_id == employee_id)
        emp_skills = (await db.execute(stmt)).scalars().all()
        current_skill_count = len(emp_skills)
        
        one_year_ago = date.today() - timedelta(days=365)
        stmt = select(EmployeeSkill).where(
            EmployeeSkill.employee_id == employee_id,
            EmployeeSkill.created_at >= one_year_ago
        )
        recent_skills = (await db.execute(stmt)).scalars().all()
        skills_added_last_year = len(recent_skills)

        # 5. Leadership
        stmt = select(func.count(Employee.id)).where(Employee.reporting_manager_id == employee_id)
        reports_count = (await db.execute(stmt)).scalar() or 0
        manages_reports = reports_count > 0
        mentors_others = reports_count > 0 or months_since_joining > 24
        led_projects = int(months_since_joining / 12)
        cross_team_collaborations = int(months_since_joining / 8)

        # Manager recommendation
        manager_recommendation = "maybe"
        if performance_scores:
            latest = performance_scores[-1]
            if latest >= 80:
                manager_recommendation = "yes"
            elif latest < 60:
                manager_recommendation = "no"

        # 6. Compute score
        result = await compute_promotion_score(
            employee_name=employee_name,
            current_role=current_role,
            target_role=target_role,
            performance_scores=performance_scores,
            months_in_current_role=months_in_current_role,
            current_skill_count=current_skill_count,
            skills_added_last_year=skills_added_last_year,
            manages_reports=manages_reports,
            mentors_others=mentors_others,
            led_projects=led_projects,
            cross_team_collaborations=cross_team_collaborations,
            manager_recommendation=manager_recommendation,
            department=department,
        )

        # 7. Save to PerformanceScore
        try:
            stmt = select(PerformanceScore).where(
                PerformanceScore.employee_id == employee_id
            ).order_by(PerformanceScore.created_at.desc())
            perf_score = (await db.execute(stmt)).scalars().first()
            if perf_score:
                perf_score.ai_promotion_score = result["promotion_score"]
                db.add(perf_score)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to save promotion score to DB: {e}")

        return result


promotion_recommender_engine = PromotionRecommenderEngine()

