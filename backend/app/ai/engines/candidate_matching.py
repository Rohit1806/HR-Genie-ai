"""
AI ENGINE 2: Candidate Matching
File: backend/app/ai/engines/candidate_matching.py
Forwards calls to backend/app/ai/engines/candidate_match.py.
"""

from app.ai.engines.candidate_match import (
    match_candidate_to_job,
    compute_skill_match,
    compute_experience_score,
    compute_semantic_similarity,
)
