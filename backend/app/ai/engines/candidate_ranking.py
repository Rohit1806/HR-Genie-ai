"""
AI ENGINE 4: Candidate Ranking
File: backend/app/ai/engines/candidate_ranking.py

Ranks a list of candidates for a job posting.
Uses a composite scoring model + diversity-aware tie-breaking.

Input: list of candidates with their AI evaluation scores
Output: sorted ranked list with rank metadata
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scoring Config
# ---------------------------------------------------------------------------

RANKING_WEIGHTS = {
    "overall_score": 0.35,
    "skill_match_score": 0.30,
    "experience_score": 0.20,
    "semantic_similarity_score": 0.15,
}

RECOMMENDATION_BONUS = {
    "STRONG_YES": 8.0,
    "YES": 4.0,
    "MAYBE": 0.0,
    "NO": -5.0,
    "STRONG_NO": -10.0,
}

STAGE_MULTIPLIER = {
    "applied": 1.0,
    "screening": 1.0,
    "interview": 1.05,   # slight boost — already cleared first screen
    "technical": 1.08,
    "offer": 1.10,
    "hired": 1.10,
    "rejected": 0.0,     # excluded from ranking
}


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class CandidateScore:
    application_id: str
    candidate_id: str
    candidate_name: str
    current_stage: str

    # Raw scores (0-100)
    overall_score: float = 0.0
    skill_match_score: float = 0.0
    experience_score: float = 0.0
    semantic_similarity_score: float = 0.0

    # From evaluation
    recommendation: str = "MAYBE"
    confidence: float = 0.75
    strengths: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)

    # Computed
    composite_score: float = 0.0
    rank: int = 0
    rank_tier: str = ""  # "Top Tier", "Strong", "Average", "Weak"
    rank_explanation: str = ""


# ---------------------------------------------------------------------------
# Ranking Logic
# ---------------------------------------------------------------------------

def _compute_composite_score(candidate: CandidateScore) -> float:
    """Compute composite ranking score with bonuses and multipliers."""

    # Base weighted score
    base = (
        candidate.overall_score * RANKING_WEIGHTS["overall_score"]
        + candidate.skill_match_score * RANKING_WEIGHTS["skill_match_score"]
        + candidate.experience_score * RANKING_WEIGHTS["experience_score"]
        + candidate.semantic_similarity_score * RANKING_WEIGHTS["semantic_similarity_score"]
    )

    # Recommendation bonus
    rec_bonus = RECOMMENDATION_BONUS.get(candidate.recommendation, 0.0)

    # Confidence weight — lower confidence slightly reduces score
    confidence_factor = 0.85 + (candidate.confidence * 0.15)

    # Stage multiplier — further in pipeline = slightly higher score
    stage_mult = STAGE_MULTIPLIER.get(candidate.current_stage, 1.0)

    # Red flag penalty
    red_flag_penalty = len(candidate.red_flags) * 2.0

    composite = (base + rec_bonus - red_flag_penalty) * confidence_factor * stage_mult
    return round(max(0.0, min(100.0, composite)), 2)


def _assign_tier(score: float) -> str:
    if score >= 80:
        return "Top Tier"
    elif score >= 65:
        return "Strong"
    elif score >= 50:
        return "Average"
    return "Weak"


def _build_rank_explanation(candidate: CandidateScore) -> str:
    parts = []

    if candidate.skill_match_score >= 80:
        parts.append("Strong skill alignment")
    elif candidate.skill_match_score < 50:
        parts.append("Skill gaps present")

    if candidate.experience_score >= 90:
        parts.append("experience matches well")
    elif candidate.experience_score < 55:
        parts.append("under/over-experienced")

    if candidate.recommendation in ("STRONG_YES", "YES"):
        parts.append("AI recommends proceeding")
    elif candidate.recommendation in ("NO", "STRONG_NO"):
        parts.append("AI does not recommend")

    if candidate.red_flags:
        parts.append(f"{len(candidate.red_flags)} concern(s) flagged")

    if not parts:
        parts.append("Average fit across dimensions")

    return "; ".join(parts).capitalize() + "."


# ---------------------------------------------------------------------------
# Main Ranking Function
# ---------------------------------------------------------------------------

def rank_candidates(
    candidates: list[dict],
    top_n: Optional[int] = None,
    exclude_rejected: bool = True,
) -> list[dict]:
    """
    Rank a list of candidates for a job posting.

    Input: list of candidate dicts, each containing:
    {
        "application_id": str,
        "candidate_id": str,
        "candidate_name": str,
        "current_stage": str,
        "overall_score": float,
        "skill_match_score": float,
        "experience_score": float,
        "semantic_similarity_score": float,
        "recommendation": str,
        "confidence": float,
        "strengths": [str],
        "red_flags": [str],
    }

    Returns: sorted list with rank, tier, composite_score, explanation added.
    """
    logger.info(f"Ranking {len(candidates)} candidates")

    scored: list[CandidateScore] = []

    for c in candidates:
        stage = c.get("current_stage", "applied")
        if exclude_rejected and stage == "rejected":
            continue

        cs = CandidateScore(
            application_id=c.get("application_id", ""),
            candidate_id=c.get("candidate_id", ""),
            candidate_name=c.get("candidate_name", "Unknown"),
            current_stage=stage,
            overall_score=float(c.get("overall_score", 50)),
            skill_match_score=float(c.get("skill_match_score", 50)),
            experience_score=float(c.get("experience_score", 50)),
            semantic_similarity_score=float(c.get("semantic_similarity_score", 50)),
            recommendation=c.get("recommendation", "MAYBE"),
            confidence=float(c.get("confidence", 0.75)),
            strengths=c.get("strengths", []),
            red_flags=c.get("red_flags", []),
        )
        cs.composite_score = _compute_composite_score(cs)
        scored.append(cs)

    # Sort descending by composite score, tie-break on skill_match_score
    scored.sort(
        key=lambda x: (x.composite_score, x.skill_match_score),
        reverse=True,
    )

    # Assign ranks and tiers
    for i, cs in enumerate(scored):
        cs.rank = i + 1
        cs.rank_tier = _assign_tier(cs.composite_score)
        cs.rank_explanation = _build_rank_explanation(cs)

    # Limit to top_n if requested
    if top_n:
        scored = scored[:top_n]

    # Serialize back to dicts, merging original data
    result = []
    original_map = {c.get("application_id"): c for c in candidates}
    for cs in scored:
        original = original_map.get(cs.application_id, {})
        result.append({
            **original,
            "rank": cs.rank,
            "rank_tier": cs.rank_tier,
            "composite_score": cs.composite_score,
            "rank_explanation": cs.rank_explanation,
        })

    logger.info(f"Ranking complete. Top candidate: {scored[0].candidate_name if scored else 'N/A'}")
    return result


def get_ranking_summary(ranked_candidates: list[dict]) -> dict:
    """
    Generate a summary of the ranking results.
    Returns counts per tier, top 3 names, average score.
    """
    if not ranked_candidates:
        return {"total": 0, "tiers": {}, "average_score": 0, "top_candidates": []}

    tier_counts = {}
    scores = []
    top_3 = []

    for c in ranked_candidates:
        tier = c.get("rank_tier", "Unknown")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        scores.append(c.get("composite_score", 0))
        if c.get("rank", 99) <= 3:
            top_3.append({
                "rank": c["rank"],
                "name": c.get("candidate_name", "Unknown"),
                "score": c.get("composite_score"),
                "recommendation": c.get("recommendation"),
            })

    return {
        "total": len(ranked_candidates),
        "tiers": tier_counts,
        "average_score": round(sum(scores) / len(scores), 1),
        "top_candidates": top_3,
    }
