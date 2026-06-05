"""
AI ENGINE 9: Performance Insight
File: backend/app/ai/engines/performance_insight.py

Generates AI-powered insights from performance review data:
- Narrative summary of performance cycle results
- Trend analysis across multiple cycles
- Strength/development area identification
- Manager coaching recommendations
- Team performance health check
"""

import logging
from typing import Optional
import statistics

from app.ai.gemini_client import call_gemini_json, call_gemini

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Score Interpretation
# ---------------------------------------------------------------------------

PERFORMANCE_BANDS = {
    "exceptional": (90, 100),
    "exceeds_expectations": (75, 89),
    "meets_expectations": (55, 74),
    "needs_improvement": (35, 54),
    "below_expectations": (0, 34),
}


def score_to_band(score: float) -> str:
    for band, (low, high) in PERFORMANCE_BANDS.items():
        if low <= score <= high:
            return band
    return "meets_expectations"


def band_to_label(band: str) -> str:
    return {
        "exceptional": "Exceptional",
        "exceeds_expectations": "Exceeds Expectations",
        "meets_expectations": "Meets Expectations",
        "needs_improvement": "Needs Improvement",
        "below_expectations": "Below Expectations",
    }.get(band, "Meets Expectations")


# ---------------------------------------------------------------------------
# Individual Performance Insight
# ---------------------------------------------------------------------------

async def generate_individual_insight(
    employee_name: str,
    current_cycle_name: str,
    goal_score: float,
    self_score: float,
    manager_score: float,
    competency_ratings: dict,     # {"communication": 4, "technical": 5, ...}
    manager_feedback: str,
    self_feedback: str,
    historical_scores: list[dict],  # [{"cycle": str, "final_score": float}]
) -> dict:
    """
    Generate AI insight for an individual employee's performance review.

    Returns:
    {
        "final_score": float,
        "performance_band": str,
        "band_label": str,
        "score_trend": str,         # "improving", "declining", "stable"
        "top_strengths": [str],
        "development_areas": [str],
        "manager_coaching_tips": [str],
        "ai_narrative": str,        # 4-5 sentence executive summary
        "self_manager_alignment": float,  # how close self vs manager score
        "key_achievements": [str],
        "next_cycle_goals": [str],
    }
    """
    logger.info(f"Generating performance insight for: {employee_name}")

    # Weighted final score: goal 30%, manager 50%, self 20%
    final_score = round(goal_score * 0.30 + manager_score * 0.50 + self_score * 0.20, 1)
    band = score_to_band(final_score)

    # Self-manager alignment (lower = more agreement)
    alignment_delta = abs(manager_score - self_score)
    alignment_score = round(max(0, 100 - alignment_delta * 2), 1)

    # Trend analysis
    trend = _compute_trend(historical_scores, final_score)

    # Top competencies
    if competency_ratings:
        sorted_comp = sorted(competency_ratings.items(), key=lambda x: x[1], reverse=True)
        top_strengths_raw = [k.replace("_", " ").title() for k, v in sorted_comp[:3] if v >= 4]
        dev_areas_raw = [k.replace("_", " ").title() for k, v in sorted_comp if v <= 2]
    else:
        top_strengths_raw = []
        dev_areas_raw = []

    # Build historical context string for AI
    hist_str = ", ".join(
        f"{h['cycle']}: {h['final_score']:.0f}"
        for h in (historical_scores or [])[-3:]
    ) or "First cycle"

    prompt = f"""
You are an expert HR performance analyst. Generate insights for this employee review.

Employee: {employee_name}
Cycle: {current_cycle_name}
Final Score: {final_score}/100 ({band_to_label(band)})
Goal Score: {goal_score}/100
Self Assessment: {self_score}/100
Manager Rating: {manager_score}/100
Historical Scores: {hist_str}
Trend: {trend}

Top Competencies: {', '.join(f"{k}: {v}/5" for k, v in (competency_ratings or {}).items())}

Manager's Feedback Summary: {manager_feedback[:500] if manager_feedback else 'Not provided'}
Self Assessment Summary: {self_feedback[:300] if self_feedback else 'Not provided'}

Return a JSON object:
{{
  "ai_narrative": "4-5 sentence professional performance summary",
  "top_strengths": ["strength 1", "strength 2", "strength 3"],
  "development_areas": ["area 1", "area 2"],
  "manager_coaching_tips": ["tip 1", "tip 2", "tip 3"],
  "key_achievements": ["achievement 1", "achievement 2"],
  "next_cycle_goals": ["goal 1", "goal 2", "goal 3"]
}}

Be specific, actionable, and constructive. Avoid generic statements.
Return only valid JSON, no markdown.
"""

    try:
        result = await call_gemini_json(prompt)
        return {
            "final_score": final_score,
            "performance_band": band,
            "band_label": band_to_label(band),
            "score_trend": trend,
            "top_strengths": result.get("top_strengths", top_strengths_raw),
            "development_areas": result.get("development_areas", dev_areas_raw),
            "manager_coaching_tips": result.get("manager_coaching_tips", []),
            "ai_narrative": result.get("ai_narrative", f"{employee_name} completed the {current_cycle_name} review cycle with a score of {final_score}/100."),
            "self_manager_alignment": alignment_score,
            "key_achievements": result.get("key_achievements", []),
            "next_cycle_goals": result.get("next_cycle_goals", []),
        }

    except Exception as e:
        logger.error(f"Performance insight generation failed: {e}")
        return {
            "final_score": final_score,
            "performance_band": band,
            "band_label": band_to_label(band),
            "score_trend": trend,
            "top_strengths": top_strengths_raw,
            "development_areas": dev_areas_raw,
            "manager_coaching_tips": [],
            "ai_narrative": f"{employee_name} completed the {current_cycle_name} cycle with a score of {final_score:.0f}/100 ({band_to_label(band)}).",
            "self_manager_alignment": alignment_score,
            "key_achievements": [],
            "next_cycle_goals": [],
        }


# ---------------------------------------------------------------------------
# Team Performance Health Check
# ---------------------------------------------------------------------------

async def generate_team_performance_summary(
    manager_name: str,
    team_members: list[dict],  # [{"name": str, "final_score": float, "band": str, "trend": str}]
    cycle_name: str,
) -> dict:
    """
    Generate a team-level performance health check for a manager.

    Returns:
    {
        "team_avg_score": float,
        "distribution": {band: count},
        "top_performers": [str],
        "at_risk_employees": [str],
        "team_trend": str,
        "ai_team_summary": str,
        "manager_action_items": [str],
    }
    """
    if not team_members:
        return {"error": "No team members provided"}

    scores = [m.get("final_score", 0) for m in team_members]
    avg_score = round(statistics.mean(scores), 1)

    distribution = {}
    for m in team_members:
        band = m.get("band", score_to_band(m.get("final_score", 50)))
        distribution[band] = distribution.get(band, 0) + 1

    top_performers = [
        m["name"] for m in team_members
        if m.get("final_score", 0) >= 80
    ]
    at_risk = [
        m["name"] for m in team_members
        if m.get("final_score", 100) < 50
    ]

    team_summary_text = "\n".join(
        f"- {m['name']}: {m.get('final_score', 'N/A')}/100 ({m.get('band', 'N/A')})"
        for m in team_members
    )

    prompt = f"""
You are an HR analytics expert. Summarize team performance and advise the manager.

Manager: {manager_name}
Cycle: {cycle_name}
Team Average Score: {avg_score}/100
Team Size: {len(team_members)}

Individual Scores:
{team_summary_text}

Return JSON:
{{
  "ai_team_summary": "3-4 sentence team performance narrative for the manager",
  "manager_action_items": ["action 1", "action 2", "action 3"],
  "recognition_suggestions": ["who to recognize and why"],
  "intervention_needed": ["who needs immediate support and why"]
}}
Return only valid JSON, no markdown.
"""

    try:
        result = await call_gemini_json(prompt)
    except Exception as e:
        logger.error(f"Team summary generation failed: {e}")
        result = {}

    return {
        "team_avg_score": avg_score,
        "team_size": len(team_members),
        "distribution": distribution,
        "top_performers": top_performers,
        "at_risk_employees": at_risk,
        "team_trend": _compute_team_trend(team_members),
        "ai_team_summary": result.get(
            "ai_team_summary",
            f"{manager_name}'s team averaged {avg_score}/100 in {cycle_name}."
        ),
        "manager_action_items": result.get("manager_action_items", []),
        "recognition_suggestions": result.get("recognition_suggestions", []),
        "intervention_needed": result.get("intervention_needed", []),
    }


# ---------------------------------------------------------------------------
# Trend Helpers
# ---------------------------------------------------------------------------

def _compute_trend(historical_scores: list[dict], current_score: float) -> str:
    if not historical_scores or len(historical_scores) < 2:
        return "stable"

    past_scores = [h["final_score"] for h in historical_scores[-2:]]
    avg_past = sum(past_scores) / len(past_scores)

    delta = current_score - avg_past
    if delta > 5:
        return "improving"
    elif delta < -5:
        return "declining"
    return "stable"


def _compute_team_trend(team_members: list[dict]) -> str:
    improving = sum(1 for m in team_members if m.get("trend") == "improving")
    declining = sum(1 for m in team_members if m.get("trend") == "declining")
    total = len(team_members)
    if total == 0:
        return "stable"
    if improving / total > 0.5:
        return "improving"
    elif declining / total > 0.4:
        return "declining"
    return "stable"


# ---------------------------------------------------------------------------
# Bell Curve Distribution (for Analytics Dashboard)
# ---------------------------------------------------------------------------

def compute_performance_distribution(all_scores: list[float]) -> dict:
    """
    Compute performance distribution for bell curve visualization.

    Returns bin counts suitable for Recharts BarChart.
    """
    if not all_scores:
        return {"bins": [], "mean": 0, "std_dev": 0}

    bins = [
        {"range": "0-20", "min": 0, "max": 20, "count": 0, "label": "Below Expectations"},
        {"range": "21-40", "min": 21, "max": 40, "count": 0, "label": "Needs Improvement"},
        {"range": "41-60", "min": 41, "max": 60, "count": 0, "label": "Meets Expectations"},
        {"range": "61-80", "min": 61, "max": 80, "count": 0, "label": "Exceeds Expectations"},
        {"range": "81-100", "min": 81, "max": 100, "count": 0, "label": "Exceptional"},
    ]

    for score in all_scores:
        for b in bins:
            if b["min"] <= score <= b["max"]:
                b["count"] += 1
                break

    mean = round(statistics.mean(all_scores), 1)
    std_dev = round(statistics.stdev(all_scores), 1) if len(all_scores) > 1 else 0

    return {
        "bins": bins,
        "mean": mean,
        "std_dev": std_dev,
        "total": len(all_scores),
    }
