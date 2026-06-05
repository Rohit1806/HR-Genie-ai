"""
AI ENGINE 8: Skill Gap Analyzer
File: backend/app/ai/engines/skill_gap_analyzer.py

Analyzes skill gaps for:
1. Individual employees vs their current role or target role
2. Teams vs project requirements
3. Department vs industry benchmarks

Produces:
- Gap assessment per skill
- Learning recommendations with resources
- Priority ranking of skills to acquire
- Timeline estimates
"""

import logging
from typing import Optional

from app.ai.gemini_client import call_gemini_json
from app.ai.embeddings import encode, cosine_similarity

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Proficiency Levels
# ---------------------------------------------------------------------------

PROFICIENCY_SCALE = {
    "beginner": 1,
    "elementary": 2,
    "intermediate": 3,
    "advanced": 4,
    "expert": 5,
}

PROFICIENCY_LABELS = {v: k for k, v in PROFICIENCY_SCALE.items()}

MONTHS_TO_ADVANCE = {
    # (from_level, to_level): months estimate
    (1, 2): 2,
    (1, 3): 6,
    (1, 4): 18,
    (1, 5): 36,
    (2, 3): 3,
    (2, 4): 12,
    (2, 5): 24,
    (3, 4): 8,
    (3, 5): 18,
    (4, 5): 12,
}


def months_to_close_gap(current_level: int, required_level: int) -> int:
    if current_level >= required_level:
        return 0
    return MONTHS_TO_ADVANCE.get((current_level, required_level), (required_level - current_level) * 6)


# ---------------------------------------------------------------------------
# Skill Normalization & Grouping
# ---------------------------------------------------------------------------

SKILL_CATEGORIES = {
    "programming_languages": ["python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "r"],
    "frameworks": ["react", "angular", "vue", "fastapi", "django", "spring", "node.js", "next.js"],
    "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra"],
    "cloud_devops": ["aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd", "github actions"],
    "ai_ml": ["machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn"],
    "data": ["sql", "spark", "airflow", "tableau", "power bi", "pandas", "data engineering"],
    "soft_skills": ["leadership", "communication", "project management", "agile", "scrum"],
}


def categorize_skill(skill_name: str) -> str:
    skill_lower = skill_name.lower()
    for category, skills in SKILL_CATEGORIES.items():
        if any(s in skill_lower for s in skills):
            return category
    return "other"


# ---------------------------------------------------------------------------
# Individual Gap Analysis
# ---------------------------------------------------------------------------

def compute_individual_gap(
    employee_skills: list[dict],  # [{"name": str, "proficiency": str, "years": float}]
    required_skills: list[dict],  # [{"name": str, "required_level": str, "priority": str}]
) -> dict:
    """
    Compute skill gap between an employee and role requirements.

    Returns:
    {
        "matched_skills": [...],
        "gap_skills": [...],        # required but missing/below level
        "surplus_skills": [...],    # employee has but not required
        "gap_score": float,         # 0-100, higher = bigger gap
        "readiness_score": float,   # 0-100, higher = more ready
        "critical_gaps": [...],     # high-priority gaps
    }
    """
    emp_skill_map = {
        s["name"].lower(): {
            "proficiency_level": PROFICIENCY_SCALE.get(
                s.get("proficiency", "intermediate").lower(), 3
            ),
            "years": float(s.get("years_experience", 0)),
        }
        for s in employee_skills
    }

    matched = []
    gaps = []
    critical_gaps = []

    for req in required_skills:
        req_name = req["name"].lower()
        req_level = PROFICIENCY_SCALE.get(req.get("required_level", "intermediate").lower(), 3)
        priority = req.get("priority", "medium")

        emp_data = emp_skill_map.get(req_name)
        if emp_data is None:
            # Skill completely missing
            gap_entry = {
                "skill": req["name"],
                "current_level": 0,
                "current_label": "none",
                "required_level": req_level,
                "required_label": PROFICIENCY_LABELS.get(req_level, "intermediate"),
                "gap_magnitude": req_level,
                "priority": priority,
                "months_to_close": months_to_close_gap(0, req_level),
                "category": categorize_skill(req["name"]),
            }
            gaps.append(gap_entry)
            if priority == "high":
                critical_gaps.append(gap_entry)
        else:
            current_level = emp_data["proficiency_level"]
            if current_level >= req_level:
                matched.append({
                    "skill": req["name"],
                    "current_level": current_level,
                    "required_level": req_level,
                    "exceeds_by": current_level - req_level,
                })
            else:
                gap_magnitude = req_level - current_level
                gap_entry = {
                    "skill": req["name"],
                    "current_level": current_level,
                    "current_label": PROFICIENCY_LABELS.get(current_level, "beginner"),
                    "required_level": req_level,
                    "required_label": PROFICIENCY_LABELS.get(req_level, "intermediate"),
                    "gap_magnitude": gap_magnitude,
                    "priority": priority,
                    "months_to_close": months_to_close_gap(current_level, req_level),
                    "category": categorize_skill(req["name"]),
                }
                gaps.append(gap_entry)
                if priority == "high":
                    critical_gaps.append(gap_entry)

    # Surplus skills (employee has, not in requirements)
    req_names = {r["name"].lower() for r in required_skills}
    surplus = [
        {"skill": s["name"], "proficiency": s.get("proficiency", "intermediate")}
        for s in employee_skills
        if s["name"].lower() not in req_names
    ]

    # Readiness score: % of required skills met fully
    total_required = len(required_skills)
    if total_required == 0:
        readiness = 100.0
        gap_score = 0.0
    else:
        fully_met = len(matched)
        readiness = round((fully_met / total_required) * 100, 1)

        # Weighted gap score (high-priority gaps count more)
        gap_weight = sum(
            g["gap_magnitude"] * (2 if g["priority"] == "high" else 1)
            for g in gaps
        )
        max_gap_weight = total_required * 5 * 2  # worst case: all high-priority, gap=5
        gap_score = round(min(100, (gap_weight / max(max_gap_weight, 1)) * 100), 1)

    return {
        "matched_skills": matched,
        "gap_skills": gaps,
        "surplus_skills": surplus,
        "gap_score": gap_score,
        "readiness_score": readiness,
        "critical_gaps": critical_gaps,
        "total_required": total_required,
        "total_matched": len(matched),
        "total_gaps": len(gaps),
    }


# ---------------------------------------------------------------------------
# AI Learning Recommendations
# ---------------------------------------------------------------------------

async def generate_learning_plan(
    employee_name: str,
    gap_analysis: dict,
    target_role: str,
    current_role: str,
    timeline_months: int = 6,
) -> dict:
    """
    Generate a personalized learning plan based on skill gap analysis.

    Returns:
    {
        "employee_name": str,
        "target_role": str,
        "timeline_months": int,
        "learning_paths": [
            {
                "skill": str,
                "priority": str,
                "resources": [{"title": str, "type": str, "url": str, "duration_hours": int}],
                "milestone": str,
                "estimated_months": int,
            }
        ],
        "quick_wins": [str],   # skills closeable in <2 months
        "ai_recommendation": str,
    }
    """
    if not gap_analysis.get("gap_skills"):
        return {
            "employee_name": employee_name,
            "target_role": target_role,
            "timeline_months": 0,
            "learning_paths": [],
            "quick_wins": [],
            "ai_recommendation": f"{employee_name} meets all skill requirements for {target_role}.",
        }

    # Build prompt context
    gap_summary = "\n".join([
        f"- {g['skill']}: currently {g.get('current_label', 'none')}, "
        f"needs {g['required_label']} ({g['priority']} priority)"
        for g in gap_analysis["gap_skills"][:8]
    ])

    prompt = f"""
You are an expert L&D consultant. Create a practical learning plan.

Employee: {employee_name}
Current Role: {current_role}
Target Role: {target_role}
Timeline: {timeline_months} months

Skill Gaps to Address:
{gap_summary}

Return a JSON object with:
{{
  "learning_paths": [
    {{
      "skill": "skill name",
      "priority": "high|medium|low",
      "resources": [
        {{"title": "course name", "type": "course|book|practice|certification", "platform": "Coursera/Udemy/etc", "estimated_hours": 20}}
      ],
      "milestone": "what success looks like",
      "estimated_months": 2
    }}
  ],
  "quick_wins": ["skill achievable fast", ...],
  "ai_recommendation": "2-3 sentence summary of recommended approach"
}}

Prioritize free/affordable resources. Focus on the {min(5, len(gap_analysis['gap_skills']))} most important gaps.
Return only valid JSON, no markdown.
"""

    try:
        result = await call_gemini_json(prompt)
        return {
            "employee_name": employee_name,
            "target_role": target_role,
            "timeline_months": timeline_months,
            "learning_paths": result.get("learning_paths", []),
            "quick_wins": result.get("quick_wins", []),
            "ai_recommendation": result.get("ai_recommendation", ""),
        }
    except Exception as e:
        logger.error(f"Learning plan generation failed: {e}")
        # Fallback: return gap skills as learning paths without resources
        paths = [
            {
                "skill": g["skill"],
                "priority": g["priority"],
                "resources": [],
                "milestone": f"Reach {g['required_label']} level",
                "estimated_months": g["months_to_close"],
            }
            for g in gap_analysis["gap_skills"][:5]
        ]
        return {
            "employee_name": employee_name,
            "target_role": target_role,
            "timeline_months": timeline_months,
            "learning_paths": paths,
            "quick_wins": [],
            "ai_recommendation": "Manual review recommended. AI plan generation temporarily unavailable.",
        }


# ---------------------------------------------------------------------------
# Team-Level Gap Analysis
# ---------------------------------------------------------------------------

def analyze_team_gap(
    team_members: list[dict],  # each has "name", "skills" list
    project_requirements: list[dict],  # required skills for a project
) -> dict:
    """
    Analyze collective skill coverage of a team against project needs.

    Returns team-level gap report with coverage percentage per skill.
    """
    if not team_members:
        return {"error": "No team members provided"}

    skill_coverage = {}
    for req in project_requirements:
        req_name = req["name"].lower()
        req_level = PROFICIENCY_SCALE.get(req.get("required_level", "intermediate").lower(), 3)

        covering_members = []
        for member in team_members:
            member_skills = {
                s["name"].lower(): PROFICIENCY_SCALE.get(s.get("proficiency", "beginner").lower(), 1)
                for s in member.get("skills", [])
            }
            member_level = member_skills.get(req_name, 0)
            if member_level >= req_level:
                covering_members.append(member["name"])

        coverage_pct = round(len(covering_members) / len(team_members) * 100, 1)
        skill_coverage[req["name"]] = {
            "required_level": PROFICIENCY_LABELS.get(req_level, "intermediate"),
            "covered_by": covering_members,
            "coverage_percent": coverage_pct,
            "is_gap": coverage_pct < 30,  # gap if fewer than 30% of team has it
        }

    gaps = [k for k, v in skill_coverage.items() if v["is_gap"]]
    team_readiness = round(
        sum(v["coverage_percent"] for v in skill_coverage.values()) / max(len(skill_coverage), 1),
        1,
    )

    return {
        "team_size": len(team_members),
        "skill_coverage": skill_coverage,
        "team_readiness_score": team_readiness,
        "coverage_gaps": gaps,
        "recommendations": [
            f"Hire or upskill for: {', '.join(gaps[:3])}" if gaps else "Team is well-equipped for this project."
        ],
    }
