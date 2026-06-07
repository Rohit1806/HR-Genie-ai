"""
AI ENGINE 12: Attrition Predictor
File: backend/app/ai/engines/attrition_predictor.py

Predicts employee attrition risk using a rule-based scoring model
combined with AI narrative analysis.

Risk factors considered:
- Performance trend (declining = high risk)
- Tenure in role (too short or too long = risk)
- Leave patterns (excessive unplanned leaves)
- Salary competitiveness (estimated)
- Manager relationship signals
- Recent promotion status
- Engagement indicators
- Department attrition history

Outputs: risk_score (0-100), risk_level, top risk factors, recommended interventions.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional

from app.ai.gemini_client import call_gemini_json
from app.ai.prompts.attrition_analysis import ATTRITION_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Risk Factor Definitions
# ---------------------------------------------------------------------------

class RiskFactor:
    def __init__(self, name: str, weight: float, description: str):
        self.name = name
        self.weight = weight
        self.description = description


RISK_FACTORS = [
    RiskFactor("performance_decline", 0.20, "Performance score dropped >10 points last cycle"),
    RiskFactor("long_tenure_no_promotion", 0.18, "In role >24 months without promotion"),
    RiskFactor("low_performance", 0.15, "Current performance score below 55"),
    RiskFactor("excessive_unplanned_leave", 0.12, "Unplanned leaves >3x average in last 3 months"),
    RiskFactor("salary_below_market", 0.12, "Estimated salary below market by >20%"),
    RiskFactor("manager_conflict_signals", 0.10, "Low self-manager alignment score (<60)"),
    RiskFactor("department_high_attrition", 0.08, "Works in a department with >15% attrition"),
    RiskFactor("no_recent_recognition", 0.05, "No recognition or achievement in past 6 months"),
]

TOTAL_MAX_WEIGHT = sum(f.weight for f in RISK_FACTORS)  # Should be 1.0

RISK_LEVELS = {
    "critical": (80, 100),
    "high": (60, 79),
    "medium": (40, 59),
    "low": (0, 39),
}


def score_to_risk_level(score: float) -> str:
    for level, (low, high) in RISK_LEVELS.items():
        if low <= score <= high:
            return level
    return "low"


# ---------------------------------------------------------------------------
# Individual Risk Scoring
# ---------------------------------------------------------------------------

def compute_attrition_risk(
    employee_name: str,
    months_in_current_role: int,
    last_promotion_months_ago: Optional[int],
    performance_scores: list[float],       # recent cycles, newest last
    unplanned_leaves_last_3m: int,
    team_avg_unplanned_leaves: float,
    estimated_salary: float,
    market_salary_estimate: float,
    self_manager_alignment_score: float,   # 0-100
    department_attrition_rate: float,      # percentage
    had_recognition_last_6m: bool,
) -> dict:
    """
    Compute rule-based attrition risk score.

    Returns:
    {
        "risk_score": float,
        "risk_level": str,
        "triggered_factors": [{"factor": str, "description": str, "weight": float}],
        "protective_factors": [str],
        "raw_signals": dict,
    }
    """
    logger.info(f"Computing attrition risk for: {employee_name}")

    triggered = []
    raw_signals = {}

    # 1. Performance decline
    if len(performance_scores) >= 2:
        decline = performance_scores[-2] - performance_scores[-1]
        raw_signals["performance_decline"] = decline
        if decline > 10:
            triggered.append(("performance_decline", min(1.0, decline / 20)))
    elif performance_scores:
        raw_signals["performance_decline"] = 0

    # 2. Long tenure without promotion
    raw_signals["months_in_role"] = months_in_current_role
    raw_signals["last_promotion_months_ago"] = last_promotion_months_ago
    if months_in_current_role > 24 and (last_promotion_months_ago is None or last_promotion_months_ago > 24):
        multiplier = min(1.0, (months_in_current_role - 24) / 24)
        triggered.append(("long_tenure_no_promotion", multiplier))

    # 3. Low current performance
    if performance_scores:
        current_perf = performance_scores[-1]
        raw_signals["current_performance"] = current_perf
        if current_perf < 55:
            severity = (55 - current_perf) / 55
            triggered.append(("low_performance", severity))

    # 4. Excessive unplanned leave
    raw_signals["unplanned_leaves_last_3m"] = unplanned_leaves_last_3m
    if team_avg_unplanned_leaves > 0:
        leave_ratio = unplanned_leaves_last_3m / team_avg_unplanned_leaves
        if leave_ratio > 3:
            triggered.append(("excessive_unplanned_leave", min(1.0, leave_ratio / 5)))

    # 5. Salary below market
    raw_signals["salary_gap_pct"] = 0
    if market_salary_estimate > 0 and estimated_salary > 0:
        salary_gap_pct = (market_salary_estimate - estimated_salary) / market_salary_estimate * 100
        raw_signals["salary_gap_pct"] = round(salary_gap_pct, 1)
        if salary_gap_pct > 20:
            triggered.append(("salary_below_market", min(1.0, salary_gap_pct / 50)))

    # 6. Manager conflict signals
    raw_signals["self_manager_alignment"] = self_manager_alignment_score
    if self_manager_alignment_score < 60:
        severity = (60 - self_manager_alignment_score) / 60
        triggered.append(("manager_conflict_signals", severity))

    # 7. Department high attrition
    raw_signals["dept_attrition_rate"] = department_attrition_rate
    if department_attrition_rate > 15:
        triggered.append(("department_high_attrition", min(1.0, department_attrition_rate / 30)))

    # 8. No recent recognition
    raw_signals["had_recognition_last_6m"] = had_recognition_last_6m
    if not had_recognition_last_6m:
        triggered.append(("no_recent_recognition", 1.0))

    # Compute risk score
    factor_map = {f.name: f for f in RISK_FACTORS}
    total_risk = 0.0
    triggered_details = []

    for factor_name, severity in triggered:
        factor = factor_map.get(factor_name)
        if factor:
            contribution = factor.weight * severity * 100
            total_risk += contribution
            triggered_details.append({
                "factor": factor_name,
                "description": factor.description,
                "weight": factor.weight,
                "severity": round(severity, 2),
                "contribution": round(contribution, 1),
            })

    risk_score = round(min(100, total_risk), 1)

    # Protective factors
    protective = []
    if performance_scores and performance_scores[-1] >= 80:
        protective.append("High current performance score")
    if months_in_current_role < 12:
        protective.append("Recently joined — still in growth phase")
    if last_promotion_months_ago is not None and last_promotion_months_ago < 12:
        protective.append("Recently promoted")
    if had_recognition_last_6m:
        protective.append("Recognized for contributions recently")
    if self_manager_alignment_score >= 80:
        protective.append("Strong manager relationship")
    if len(performance_scores) >= 2 and performance_scores[-1] > performance_scores[-2]:
        protective.append("Performance trending upward")

    return {
        "risk_score": risk_score,
        "risk_level": score_to_risk_level(risk_score),
        "triggered_factors": triggered_details,
        "protective_factors": protective,
        "raw_signals": raw_signals,
    }


# ---------------------------------------------------------------------------
# AI Narrative + Interventions
# ---------------------------------------------------------------------------

async def analyze_attrition_risk(
    employee_name: str,
    department: str,
    current_role: str,
    risk_result: dict,
    manager_name: str = "the manager",
) -> dict:
    """
    Enrich rule-based risk result with AI narrative and interventions.

    Returns merged dict with:
    - All fields from risk_result
    - ai_risk_summary: str
    - recommended_interventions: [str]
    - urgency: str
    - estimated_flight_risk_months: int | None
    """
    risk_score = risk_result["risk_score"]
    risk_level = risk_result["risk_level"]
    factors = risk_result.get("triggered_factors", [])
    protective = risk_result.get("protective_factors", [])

    factor_summary = "\n".join(
        f"- {f['description']} (severity: {f['severity']:.0%})"
        for f in factors[:5]
    ) or "No significant risk factors detected"

    protective_summary = "\n".join(f"- {p}" for p in protective[:3]) or "None identified"

    prompt = ATTRITION_ANALYSIS_PROMPT.format(
        employee_name=employee_name,
        department=department,
        current_role=current_role,
        risk_score=risk_score,
        risk_level=risk_level,
        factor_summary=factor_summary,
        protective_summary=protective_summary,
        manager_name=manager_name,
    )

    try:
        ai_result = await call_gemini_json(prompt)
        interventions = ai_result.get("recommended_interventions", [])
        ai_summary = ai_result.get("ai_risk_summary", "")
        urgency = ai_result.get("urgency", "medium")
        flight_months = ai_result.get("estimated_flight_risk_months")
    except Exception as e:
        logger.error(f"Attrition AI analysis failed for {employee_name}: {e}")
        interventions = _default_interventions(risk_level)
        ai_summary = f"{employee_name} has a {risk_level} attrition risk (score: {risk_score}/100)."
        urgency = "high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low"
        flight_months = None

    return {
        **risk_result,
        "ai_risk_summary": ai_summary,
        "recommended_interventions": interventions,
        "urgency": urgency,
        "estimated_flight_risk_months": flight_months,
    }


def _default_interventions(risk_level: str) -> list[str]:
    base = {
        "critical": [
            "Schedule urgent 1:1 with employee this week",
            "Review and adjust compensation if below market",
            "Discuss career progression path immediately",
            "Consider retention bonus if eligible",
        ],
        "high": [
            "Schedule 1:1 meeting within 2 weeks",
            "Discuss career goals and development plan",
            "Review workload and team dynamics",
            "Provide recognition for recent contributions",
        ],
        "medium": [
            "Ensure regular 1:1 cadence is maintained",
            "Check in on career development goals",
            "Consider skill development opportunities",
        ],
        "low": [
            "Maintain current engagement practices",
            "Continue recognition and feedback rhythm",
        ],
    }
    return base.get(risk_level, ["Monitor and check in regularly"])


# ---------------------------------------------------------------------------
# Batch Risk Analysis (for Analytics Dashboard Heatmap)
# ---------------------------------------------------------------------------

def batch_compute_risk_scores(
    employees: list[dict],
) -> list[dict]:
    """
    Compute risk scores for a list of employees using simplified signals.
    Used for the department heatmap on the analytics dashboard.

    Each employee dict should have:
    performance_score, months_in_role, last_promotion_months_ago,
    unplanned_leaves_last_3m, department

    Returns employees list with risk_score and risk_level added.
    """
    results = []
    for emp in employees:
        perf = emp.get("performance_score", 65)
        months = emp.get("months_in_role", 12)
        last_promo = emp.get("last_promotion_months_ago", 18)
        leaves = emp.get("unplanned_leaves_last_3m", 1)

        # Simplified scoring for batch
        score = 20.0  # base

        if perf < 55:
            score += 25
        elif perf < 70:
            score += 10

        if months > 24 and last_promo > 24:
            score += 20
        elif months > 36:
            score += 10

        if leaves > 4:
            score += 20
        elif leaves > 2:
            score += 10

        score = round(min(100, score), 1)
        results.append({
            **emp,
            "risk_score": score,
            "risk_level": score_to_risk_level(score),
        })

    return sorted(results, key=lambda x: -x["risk_score"])


# ---------------------------------------------------------------------------
# Engine wrapper class and instance export
# ---------------------------------------------------------------------------

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal

class AttritionPredictorEngine:
    async def predict_attrition(self, employee_id: uuid.UUID, db: AsyncSession) -> dict:
        try:
            from app.models.employee import Employee, EmployeeSkill, Skill, EmploymentHistory
            from app.models.leave import LeaveRequest, LeaveStatus
            from app.models.payroll import EmployeeSalary
            from app.models.performance import PerformanceScore, PerformanceReview, ReviewType
            from sqlalchemy import select, func
            from datetime import date, timedelta
            
            # 1. Fetch Employee
            employee = await db.get(Employee, employee_id)
            if not employee:
                return {"error": "Employee not found"}
                
            employee_name = employee.full_name
            department = employee.department.name if employee.department else "Unassigned"
            current_role = employee.designation.name if employee.designation else "Employee"
            manager_name = employee.reporting_manager.full_name if employee.reporting_manager else "the manager"
            
            # 2. Months in role / promotion
            months_since_joining = int((date.today() - employee.date_of_joining).days / 30.4)
            
            stmt = select(EmploymentHistory).where(
                EmploymentHistory.employee_id == employee_id,
                EmploymentHistory.event_type.ilike("%promotion%")
            ).order_by(EmploymentHistory.effective_date.desc())
            promo_history = (await db.execute(stmt)).scalars().first()
            
            if promo_history:
                last_promotion_months_ago = int((date.today() - promo_history.effective_date).days / 30.4)
                months_in_current_role = last_promotion_months_ago
            else:
                last_promotion_months_ago = None
                months_in_current_role = months_since_joining

            # 3. Performance history
            stmt = select(PerformanceScore).where(
                PerformanceScore.employee_id == employee_id
            ).order_by(PerformanceScore.created_at.asc())
            scores = (await db.execute(stmt)).scalars().all()
            performance_scores = [float(s.final_score) for s in scores if s.final_score is not None]
            if not performance_scores:
                performance_scores = [75.0]

            # 4. Leave patterns (last 3 months)
            three_months_ago = date.today() - timedelta(days=90)
            stmt = select(func.sum(LeaveRequest.days_count)).where(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status == LeaveStatus.approved,
                LeaveRequest.from_date >= three_months_ago
            )
            unplanned_leaves = (await db.execute(stmt)).scalar() or 0.0
            unplanned_leaves_last_3m = int(unplanned_leaves)
            
            # 5. Salary competitiveness
            stmt = select(EmployeeSalary).where(
                EmployeeSalary.employee_id == employee_id
            ).order_by(EmployeeSalary.effective_from.desc())
            sal_rec = (await db.execute(stmt)).scalars().first()
            estimated_salary = float(sal_rec.gross_salary) if sal_rec else 60000.0
            
            market_salary_estimate = estimated_salary * 1.15
            if employee.designation_id:
                stmt = select(func.avg(EmployeeSalary.gross_salary)).join(Employee).where(
                    Employee.designation_id == employee.designation_id
                )
                avg_designation_salary = (await db.execute(stmt)).scalar()
                if avg_designation_salary:
                    market_salary_estimate = float(avg_designation_salary)

            # 6. Self-manager alignment score & recognition
            self_manager_alignment_score = 85.0
            
            stmt = select(PerformanceReview).where(
                PerformanceReview.employee_id == employee_id
            )
            reviews = (await db.execute(stmt)).scalars().all()
            self_review_score = None
            mgr_review_score = None
            for rev in reviews:
                if rev.review_type == ReviewType.self_review and rev.overall_score:
                    self_review_score = rev.overall_score
                elif rev.review_type == ReviewType.manager_review and rev.overall_score:
                    mgr_review_score = rev.overall_score
                    
            if self_review_score is not None and mgr_review_score is not None:
                alignment_delta = abs(mgr_review_score - self_review_score)
                self_manager_alignment_score = max(0.0, 100.0 - alignment_delta * 10)

            had_recognition_last_6m = True
            if performance_scores and performance_scores[-1] < 70:
                had_recognition_last_6m = False

            department_attrition_rate = 12.0

            # 7. Run compute_attrition_risk
            risk_result = compute_attrition_risk(
                employee_name=employee_name,
                months_in_current_role=months_in_current_role,
                last_promotion_months_ago=last_promotion_months_ago,
                performance_scores=performance_scores,
                unplanned_leaves_last_3m=unplanned_leaves_last_3m,
                team_avg_unplanned_leaves=2.0,  # Fallback to team average unplanned leaves
                estimated_salary=estimated_salary,
                market_salary_estimate=market_salary_estimate,
                self_manager_alignment_score=self_manager_alignment_score,
                department_attrition_rate=department_attrition_rate,
                had_recognition_last_6m=had_recognition_last_6m,
            )
            
            # 8. Enrich with Gemini narrative
            final_result = await analyze_attrition_risk(
                employee_name=employee_name,
                department=department,
                current_role=current_role,
                risk_result=risk_result,
                manager_name=manager_name,
            )
            
            try:
                stmt = select(PerformanceScore).where(
                    PerformanceScore.employee_id == employee_id
                ).order_by(PerformanceScore.created_at.desc())
                perf_score = (await db.execute(stmt)).scalars().first()
                if perf_score:
                    perf_score.ai_attrition_risk = final_result["risk_score"]
                    db.add(perf_score)
                    await db.commit()
            except Exception as e:
                logger.error(f"Failed to save attrition risk to DB: {e}")
                
            return final_result
        except Exception as e:
            return {"error": str(e), "message": "AI feature temporarily unavailable"}


attrition_predictor_engine = AttritionPredictorEngine()

