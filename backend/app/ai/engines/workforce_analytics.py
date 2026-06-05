"""
AI ENGINE 11: Workforce Analytics
File: backend/app/ai/engines/workforce_analytics.py

Generates AI-powered workforce analytics and insights:
- Headcount trends and forecasting
- Department composition analysis
- Hiring vs attrition balance
- Tenure distribution
- Compensation benchmarking signals
- AI narrative bullets for dashboards
"""

import logging
from datetime import date, datetime, timedelta
from collections import defaultdict
from typing import Optional
import statistics

from app.ai.gemini_client import call_gemini

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Headcount Analytics
# ---------------------------------------------------------------------------

def compute_headcount_trend(
    employee_join_dates: list[date],
    employee_termination_dates: list[Optional[date]],
    months_back: int = 12,
) -> list[dict]:
    """
    Compute monthly headcount for the last N months.
    Returns list of {month, year, headcount, net_change}.
    """
    today = date.today()
    result = []

    for i in range(months_back - 1, -1, -1):
        # First day of each month going back
        target_month = today.month - i
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1

        snapshot_date = date(target_year, target_month, 1)

        count = 0
        for join, term in zip(employee_join_dates, employee_termination_dates):
            if join <= snapshot_date:
                if term is None or term >= snapshot_date:
                    count += 1

        result.append({
            "month": snapshot_date.strftime("%b"),
            "year": target_year,
            "month_num": target_month,
            "headcount": count,
        })

    # Compute net change
    for i in range(1, len(result)):
        result[i]["net_change"] = result[i]["headcount"] - result[i - 1]["headcount"]
    if result:
        result[0]["net_change"] = 0

    return result


def compute_department_distribution(
    employees: list[dict],  # [{"department": str, "status": str}]
) -> list[dict]:
    """
    Returns department distribution for pie/bar charts.
    Only counts active employees.
    """
    dept_counts: dict[str, int] = defaultdict(int)
    for emp in employees:
        if emp.get("status") == "active":
            dept = emp.get("department", "Unassigned")
            dept_counts[dept] += 1

    total = sum(dept_counts.values())
    return [
        {
            "department": dept,
            "count": count,
            "percentage": round(count / max(total, 1) * 100, 1),
        }
        for dept, count in sorted(dept_counts.items(), key=lambda x: -x[1])
    ]


# ---------------------------------------------------------------------------
# Attrition Analytics
# ---------------------------------------------------------------------------

def compute_attrition_rate(
    total_employees: int,
    terminations_this_period: int,
    period_label: str = "monthly",
) -> dict:
    """Compute attrition rate and annualize if needed."""
    if total_employees == 0:
        return {"rate": 0, "annualized_rate": 0, "label": period_label}

    rate = round(terminations_this_period / total_employees * 100, 2)
    annualized = rate * 12 if period_label == "monthly" else rate

    benchmark = 15.0  # Industry average annual attrition ~15%

    return {
        "rate": rate,
        "annualized_rate": round(annualized, 1),
        "label": period_label,
        "vs_benchmark": round(annualized - benchmark, 1),
        "status": "above_benchmark" if annualized > benchmark else "below_benchmark",
    }


def compute_attrition_by_department(
    terminations: list[dict],  # [{"department": str, "date": date, "reason": str}]
    headcount_by_dept: dict[str, int],
) -> list[dict]:
    """Compute attrition rate broken down by department."""
    dept_terms: dict[str, int] = defaultdict(int)
    for t in terminations:
        dept_terms[t.get("department", "Unknown")] += 1

    result = []
    for dept, headcount in headcount_by_dept.items():
        terms = dept_terms.get(dept, 0)
        rate = round(terms / max(headcount, 1) * 100, 1)
        result.append({
            "department": dept,
            "headcount": headcount,
            "terminations": terms,
            "attrition_rate": rate,
            "risk_level": "high" if rate > 20 else "medium" if rate > 10 else "low",
        })

    return sorted(result, key=lambda x: -x["attrition_rate"])


# ---------------------------------------------------------------------------
# Tenure Distribution
# ---------------------------------------------------------------------------

def compute_tenure_distribution(
    join_dates: list[date],
) -> dict:
    """
    Compute tenure distribution for workforce stability analysis.
    Returns buckets: <1yr, 1-2yr, 2-5yr, 5-10yr, 10+yr
    """
    today = date.today()
    buckets = {
        "<1 Year": 0,
        "1-2 Years": 0,
        "2-5 Years": 0,
        "5-10 Years": 0,
        "10+ Years": 0,
    }

    tenures_months = []
    for join_date in join_dates:
        months = (today - join_date).days / 30.44
        tenures_months.append(months)

        years = months / 12
        if years < 1:
            buckets["<1 Year"] += 1
        elif years < 2:
            buckets["1-2 Years"] += 1
        elif years < 5:
            buckets["2-5 Years"] += 1
        elif years < 10:
            buckets["5-10 Years"] += 1
        else:
            buckets["10+ Years"] += 1

    avg_tenure_months = round(statistics.mean(tenures_months), 1) if tenures_months else 0

    return {
        "distribution": [{"range": k, "count": v} for k, v in buckets.items()],
        "avg_tenure_months": avg_tenure_months,
        "avg_tenure_years": round(avg_tenure_months / 12, 1),
        "median_tenure_months": round(statistics.median(tenures_months), 1) if tenures_months else 0,
    }


# ---------------------------------------------------------------------------
# Hiring Funnel Analytics (for HR Dashboard)
# ---------------------------------------------------------------------------

def compute_hiring_funnel(
    applications_by_stage: dict[str, int],
) -> list[dict]:
    """
    Convert stage counts into a hiring funnel with conversion rates.
    Standard stages: applied → screening → interview → technical → offer → hired
    """
    STAGE_ORDER = ["applied", "screening", "interview", "technical", "offer", "hired"]

    funnel = []
    prev_count = None

    for stage in STAGE_ORDER:
        count = applications_by_stage.get(stage, 0)
        conversion = round(count / max(prev_count, 1) * 100, 1) if prev_count else 100.0
        funnel.append({
            "stage": stage.title(),
            "count": count,
            "conversion_rate": conversion,
        })
        if count > 0:
            prev_count = count

    return funnel


# ---------------------------------------------------------------------------
# AI Narrative Bullets (for Dashboard)
# ---------------------------------------------------------------------------

async def generate_workforce_insights(
    total_employees: int,
    active_employees: int,
    open_positions: int,
    monthly_attrition_rate: float,
    avg_performance_score: float,
    headcount_trend: list[dict],
    top_attrition_depts: list[dict],
    hiring_funnel: list[dict],
) -> list[dict]:
    """
    Generate 3-5 AI narrative insight bullets for the admin dashboard.

    Returns:
    [
        {
            "type": "positive"|"warning"|"info",
            "icon": str,
            "title": str,
            "body": str,
            "action": str | None,
        }
    ]
    """
    logger.info("Generating workforce AI insights")

    # Build data summary for Gemini
    recent_trend = headcount_trend[-3:] if headcount_trend else []
    trend_summary = ", ".join(
        f"{t['month']}: {t['headcount']} ({'+' if t.get('net_change',0) >= 0 else ''}{t.get('net_change',0)})"
        for t in recent_trend
    )

    at_risk_depts = [d["department"] for d in top_attrition_depts if d.get("risk_level") == "high"]

    prompt = f"""
You are an HR analytics AI. Generate 4 actionable insight bullets for an HR dashboard.

Data:
- Total Employees: {total_employees} (Active: {active_employees})
- Open Positions: {open_positions}
- Monthly Attrition Rate: {monthly_attrition_rate}%
- Avg Performance Score: {avg_performance_score}/100
- Recent Headcount Trend: {trend_summary}
- High Attrition Departments: {', '.join(at_risk_depts) or 'None'}

Return JSON array of exactly 4 insights:
[
  {{
    "type": "positive|warning|info",
    "title": "Short headline (5-8 words)",
    "body": "1-2 sentence insight with specific data",
    "action": "Recommended action or null"
  }}
]

Mix types: at least 1 positive, 1 warning, 2 info.
Use the actual numbers. Be specific. Return only valid JSON array, no markdown.
"""

    try:
        import json
        import google.generativeai as genai
        from app.config import settings

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        insights = json.loads(text)
        return insights[:5]

    except Exception as e:
        logger.error(f"Workforce insights generation failed: {e}")
        # Fallback static insights
        return [
            {
                "type": "info",
                "title": f"{active_employees} active employees",
                "body": f"Workforce stands at {active_employees} active out of {total_employees} total employees.",
                "action": None,
            },
            {
                "type": "warning" if monthly_attrition_rate > 2 else "positive",
                "title": f"Monthly attrition: {monthly_attrition_rate}%",
                "body": f"Current monthly attrition rate is {monthly_attrition_rate}%. Industry benchmark is ~1.25%.",
                "action": "Review exit interview data" if monthly_attrition_rate > 2 else None,
            },
            {
                "type": "info",
                "title": f"{open_positions} open positions",
                "body": f"There are currently {open_positions} open roles across departments.",
                "action": "Review hiring pipeline" if open_positions > 5 else None,
            },
        ]


# ---------------------------------------------------------------------------
# Payroll Cost Trend
# ---------------------------------------------------------------------------

def compute_payroll_cost_trend(
    payroll_runs: list[dict],  # [{"month": int, "year": int, "total_gross": float, "total_net": float}]
    months_back: int = 12,
) -> list[dict]:
    """
    Format payroll runs for trend chart.
    Returns list sorted by date.
    """
    from calendar import month_abbr

    sorted_runs = sorted(payroll_runs, key=lambda x: (x["year"], x["month"]))
    return [
        {
            "label": f"{month_abbr[r['month']]} {r['year']}",
            "month": r["month"],
            "year": r["year"],
            "gross": round(r.get("total_gross", 0), 0),
            "net": round(r.get("total_net", 0), 0),
            "deductions": round(r.get("total_gross", 0) - r.get("total_net", 0), 0),
        }
        for r in sorted_runs[-months_back:]
    ]
