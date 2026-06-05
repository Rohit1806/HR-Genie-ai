"""
AI ENGINE 2: Candidate Match
File: backend/app/ai/engines/candidate_match.py

Computes semantic similarity between a candidate's resume
and a job posting using sentence-transformer embeddings +
keyword overlap scoring.

Returns a match breakdown:
- skill_match_score (0-100)
- experience_score (0-100)
- semantic_similarity_score (0-100)
- overall_match_score (0-100, weighted)
- matched_skills: [str]
- missing_skills: [str]
- match_explanation: str
"""

import logging
from typing import Optional

from app.ai.embeddings import encode, cosine_similarity

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scoring Weights
# ---------------------------------------------------------------------------
WEIGHT_SKILLS = 0.40
WEIGHT_EXPERIENCE = 0.25
WEIGHT_SEMANTIC = 0.35


# ---------------------------------------------------------------------------
# Skill Matching
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return text.strip().lower()


def compute_skill_match(
    candidate_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str] | None = None,
) -> dict:
    """
    Compare candidate skills vs job required + preferred skills.

    Returns:
    {
        "score": float 0-100,
        "matched_required": [str],
        "matched_preferred": [str],
        "missing_required": [str],
        "total_required": int,
    }
    """
    preferred_skills = preferred_skills or []

    candidate_set = {_normalize(s) for s in candidate_skills}
    required_set = {_normalize(s) for s in required_skills}
    preferred_set = {_normalize(s) for s in preferred_skills}

    matched_required = [s for s in required_skills if _normalize(s) in candidate_set]
    matched_preferred = [s for s in preferred_skills if _normalize(s) in candidate_set]
    missing_required = [s for s in required_skills if _normalize(s) not in candidate_set]

    if not required_set:
        # No required skills defined — score from semantic match only
        return {
            "score": 75.0,
            "matched_required": [],
            "matched_preferred": [],
            "missing_required": [],
            "total_required": 0,
        }

    # Required skills: 80% weight, preferred: 20% weight
    required_score = (len(matched_required) / len(required_set)) * 80
    preferred_bonus = (len(matched_preferred) / max(len(preferred_set), 1)) * 20 if preferred_set else 20

    score = min(required_score + preferred_bonus, 100.0)

    return {
        "score": round(score, 1),
        "matched_required": matched_required,
        "matched_preferred": matched_preferred,
        "missing_required": missing_required,
        "total_required": len(required_set),
    }


# ---------------------------------------------------------------------------
# Experience Scoring
# ---------------------------------------------------------------------------

def compute_experience_score(
    candidate_years: float,
    required_min: float,
    required_max: float,
) -> float:
    """
    Score candidate experience vs job requirements.
    - Below min: linearly penalized
    - In range: 100
    - Above max by ≤3 years: 95 (slight overqualification tolerance)
    - Above max by >3 years: gradually penalized (overqualified risk)
    """
    if required_max <= 0:
        return 80.0  # No requirement specified

    if candidate_years < required_min:
        if required_min == 0:
            return 100.0
        ratio = candidate_years / required_min
        score = max(20.0, ratio * 80.0)
    elif candidate_years <= required_max:
        score = 100.0
    else:
        overshoot = candidate_years - required_max
        if overshoot <= 3:
            score = 95.0
        else:
            score = max(60.0, 95.0 - (overshoot - 3) * 5)

    return round(score, 1)


# ---------------------------------------------------------------------------
# Semantic Similarity
# ---------------------------------------------------------------------------

def compute_semantic_similarity(
    resume_text: str,
    job_description: str,
) -> float:
    """
    Use sentence-transformer embeddings to compute semantic similarity.
    Returns 0-100 score.
    """
    if not resume_text or not job_description:
        return 50.0  # Neutral fallback

    # Truncate to reasonable lengths for embedding
    resume_chunk = resume_text[:1500]
    jd_chunk = job_description[:1500]

    try:
        embeddings = encode([resume_chunk, jd_chunk])
        sim = cosine_similarity(embeddings[0], embeddings[1])
        # cosine_similarity returns -1 to 1, map to 0-100
        score = (sim + 1) / 2 * 100
        return round(float(score), 1)
    except Exception as e:
        logger.warning(f"Embedding similarity failed: {e}. Using fallback 50.0")
        return 50.0


# ---------------------------------------------------------------------------
# Main Match Function
# ---------------------------------------------------------------------------

async def match_candidate_to_job(
    candidate_skills: list[str],
    candidate_experience_years: float,
    resume_text: str,
    job_title: str,
    job_description: str,
    job_requirements: str,
    required_skills: list[str],
    preferred_skills: list[str] | None = None,
    experience_min: float = 0,
    experience_max: float = 10,
) -> dict:
    """
    Full candidate-job match computation.

    Returns:
    {
        "skill_match_score": float,
        "experience_score": float,
        "semantic_similarity_score": float,
        "overall_match_score": float,
        "matched_skills": [str],
        "missing_skills": [str],
        "match_grade": str,  # A/B/C/D/F
        "match_explanation": str,
        "is_recommended": bool,
    }
    """
    logger.info(f"Computing match for job: {job_title}")

    # 1. Skill match
    skill_result = compute_skill_match(
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
    )

    # 2. Experience score
    exp_score = compute_experience_score(
        candidate_years=candidate_experience_years,
        required_min=experience_min,
        required_max=experience_max,
    )

    # 3. Semantic similarity: resume text vs full JD
    jd_full = f"{job_title}\n{job_description}\n{job_requirements}"
    semantic_score = compute_semantic_similarity(resume_text, jd_full)

    # 4. Weighted overall score
    overall = (
        skill_result["score"] * WEIGHT_SKILLS
        + exp_score * WEIGHT_EXPERIENCE
        + semantic_score * WEIGHT_SEMANTIC
    )
    overall = round(overall, 1)

    # 5. Grade
    grade = _score_to_grade(overall)

    # 6. Human-readable explanation
    explanation = _build_explanation(
        skill_result=skill_result,
        exp_score=exp_score,
        semantic_score=semantic_score,
        overall=overall,
        candidate_years=candidate_experience_years,
        required_min=experience_min,
        required_max=experience_max,
    )

    return {
        "skill_match_score": skill_result["score"],
        "experience_score": exp_score,
        "semantic_similarity_score": semantic_score,
        "overall_match_score": overall,
        "matched_skills": skill_result["matched_required"] + skill_result["matched_preferred"],
        "missing_skills": skill_result["missing_required"],
        "match_grade": grade,
        "match_explanation": explanation,
        "is_recommended": overall >= 65.0,
    }


def _score_to_grade(score: float) -> str:
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 55:
        return "C"
    elif score >= 40:
        return "D"
    return "F"


def _build_explanation(
    skill_result: dict,
    exp_score: float,
    semantic_score: float,
    overall: float,
    candidate_years: float,
    required_min: float,
    required_max: float,
) -> str:
    parts = []

    # Skills
    n_matched = len(skill_result["matched_required"])
    n_total = skill_result["total_required"]
    if n_total > 0:
        parts.append(
            f"Matches {n_matched}/{n_total} required skills "
            f"({skill_result['score']:.0f}% skill fit)."
        )
        if skill_result["missing_required"]:
            missing_preview = ", ".join(skill_result["missing_required"][:3])
            parts.append(f"Missing: {missing_preview}.")

    # Experience
    if exp_score >= 95:
        parts.append(f"Experience ({candidate_years}y) aligns well with requirement ({required_min}-{required_max}y).")
    elif exp_score < 60:
        parts.append(f"Under-experienced: has {candidate_years}y, job needs {required_min}y+.")
    else:
        parts.append(f"Experience ({candidate_years}y) partially meets requirement ({required_min}-{required_max}y).")

    # Semantic
    if semantic_score >= 70:
        parts.append("Resume content is semantically well-aligned with the job description.")
    elif semantic_score < 45:
        parts.append("Resume content shows limited alignment with the job description.")

    return " ".join(parts)
