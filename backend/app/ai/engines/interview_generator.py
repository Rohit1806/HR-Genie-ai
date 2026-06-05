"""
AI ENGINE 5: Interview Generator
File: backend/app/ai/engines/interview_generator.py

Generates tailored interview questions for a job posting.
Produces questions across multiple categories:
- Technical (role-specific)
- Behavioral (STAR-format)
- Situational
- Culture fit
- Role-specific deep-dive

Questions are difficulty-tiered and tagged by skill area.
"""

import logging
from enum import Enum
from typing import Optional

from app.ai.gemini_client import call_gemini_json
from app.ai.prompts.interview_questions import INTERVIEW_QUESTIONS_PROMPT

logger = logging.getLogger(__name__)


class QuestionCategory(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    CULTURE_FIT = "culture_fit"
    ROLE_SPECIFIC = "role_specific"
    GENERAL = "general"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ---------------------------------------------------------------------------
# Default fallback questions (used when AI call fails)
# ---------------------------------------------------------------------------

FALLBACK_QUESTIONS = {
    QuestionCategory.BEHAVIORAL: [
        {
            "question": "Tell me about a time you faced a significant challenge at work. How did you handle it?",
            "category": "behavioral",
            "difficulty": "medium",
            "skill_area": "problem_solving",
            "follow_up": "What would you do differently now?",
            "evaluation_criteria": "Look for STAR structure: Situation, Task, Action, Result.",
        },
        {
            "question": "Describe a situation where you had to collaborate with a difficult team member.",
            "category": "behavioral",
            "difficulty": "medium",
            "skill_area": "teamwork",
            "follow_up": "What was the outcome of that relationship long-term?",
            "evaluation_criteria": "Look for empathy, communication skills, and conflict resolution.",
        },
        {
            "question": "Give an example of when you took initiative beyond your defined role.",
            "category": "behavioral",
            "difficulty": "easy",
            "skill_area": "ownership",
            "follow_up": "Was that recognized by your manager?",
            "evaluation_criteria": "Look for proactiveness and self-motivation.",
        },
    ],
    QuestionCategory.CULTURE_FIT: [
        {
            "question": "What kind of work environment helps you do your best work?",
            "category": "culture_fit",
            "difficulty": "easy",
            "skill_area": "self_awareness",
            "follow_up": "How do you adapt when the environment isn't ideal?",
            "evaluation_criteria": "Alignment with remote/hybrid/fast-paced culture.",
        },
        {
            "question": "How do you handle receiving critical feedback from a manager?",
            "category": "culture_fit",
            "difficulty": "easy",
            "skill_area": "growth_mindset",
            "follow_up": "Can you give a specific example?",
            "evaluation_criteria": "Openness to feedback, resilience.",
        },
    ],
    QuestionCategory.GENERAL: [
        {
            "question": "Where do you see yourself professionally in 3-5 years?",
            "category": "general",
            "difficulty": "easy",
            "skill_area": "career_goals",
            "follow_up": "How does this role fit into that plan?",
            "evaluation_criteria": "Ambition vs. role fit alignment.",
        },
    ],
}


# ---------------------------------------------------------------------------
# Main Generator
# ---------------------------------------------------------------------------

async def generate_interview_questions(
    job_title: str,
    job_description: str,
    required_skills: list[str],
    experience_min: float,
    experience_max: float,
    department: str = "",
    question_count: int = 15,
    include_categories: Optional[list[str]] = None,
) -> dict:
    """
    Generate tailored interview questions for a job posting.

    Returns:
    {
        "job_title": str,
        "total_questions": int,
        "questions": [
            {
                "id": int,
                "question": str,
                "category": str,
                "difficulty": str,
                "skill_area": str,
                "follow_up": str,
                "evaluation_criteria": str,
                "time_allocation_minutes": int,
            }
        ],
        "interview_structure": {
            "suggested_duration_minutes": int,
            "phases": [{"phase": str, "duration": int, "categories": [str]}]
        },
        "generated_by_ai": bool,
    }
    """
    logger.info(f"Generating {question_count} interview questions for: {job_title}")

    include_categories = include_categories or [c.value for c in QuestionCategory]

    prompt = INTERVIEW_QUESTIONS_PROMPT.format(
        job_title=job_title,
        job_description=job_description[:1500],
        required_skills=", ".join(required_skills) if required_skills else "General skills",
        experience_min=experience_min,
        experience_max=experience_max,
        department=department or "General",
        question_count=question_count,
        categories=", ".join(include_categories),
    )

    try:
        result: dict = await call_gemini_json(prompt)
        questions = result.get("questions", [])

        if not questions:
            raise ValueError("Empty questions list from Gemini")

        # Validate and clean each question
        cleaned = []
        for i, q in enumerate(questions[:question_count]):
            cleaned.append({
                "id": i + 1,
                "question": q.get("question", "").strip(),
                "category": q.get("category", "general"),
                "difficulty": q.get("difficulty", "medium"),
                "skill_area": q.get("skill_area", "general"),
                "follow_up": q.get("follow_up", ""),
                "evaluation_criteria": q.get("evaluation_criteria", ""),
                "time_allocation_minutes": _estimate_time(q.get("difficulty", "medium")),
            })

        # Filter out empty questions
        cleaned = [q for q in cleaned if q["question"]]

        structure = _build_interview_structure(cleaned)

        return {
            "job_title": job_title,
            "total_questions": len(cleaned),
            "questions": cleaned,
            "interview_structure": structure,
            "generated_by_ai": True,
        }

    except Exception as e:
        logger.error(f"Interview question generation failed: {e}. Using fallback questions.")
        return _fallback_question_set(job_title, job_description, required_skills)


def _estimate_time(difficulty: str) -> int:
    return {"easy": 3, "medium": 5, "hard": 8}.get(difficulty, 5)


def _build_interview_structure(questions: list[dict]) -> dict:
    """Build a suggested interview structure from the generated questions."""
    total_time = sum(q.get("time_allocation_minutes", 5) for q in questions)
    total_time += 15  # intro + wrap-up buffer

    # Group questions by category
    category_map: dict[str, list] = {}
    for q in questions:
        cat = q.get("category", "general")
        category_map.setdefault(cat, []).append(q)

    phases = [
        {"phase": "Introduction & Rapport", "duration": 5, "categories": []},
    ]

    if "technical" in category_map or "role_specific" in category_map:
        tech_time = sum(
            q["time_allocation_minutes"]
            for q in category_map.get("technical", []) + category_map.get("role_specific", [])
        )
        phases.append({
            "phase": "Technical Assessment",
            "duration": tech_time,
            "categories": ["technical", "role_specific"],
        })

    if "behavioral" in category_map:
        beh_time = sum(q["time_allocation_minutes"] for q in category_map["behavioral"])
        phases.append({
            "phase": "Behavioral Deep Dive",
            "duration": beh_time,
            "categories": ["behavioral"],
        })

    if "situational" in category_map:
        sit_time = sum(q["time_allocation_minutes"] for q in category_map["situational"])
        phases.append({
            "phase": "Situational Scenarios",
            "duration": sit_time,
            "categories": ["situational"],
        })

    if "culture_fit" in category_map:
        cf_time = sum(q["time_allocation_minutes"] for q in category_map["culture_fit"])
        phases.append({
            "phase": "Culture & Values Alignment",
            "duration": cf_time,
            "categories": ["culture_fit"],
        })

    phases.append({"phase": "Candidate Q&A", "duration": 10, "categories": []})

    return {
        "suggested_duration_minutes": total_time,
        "phases": phases,
    }


def _fallback_question_set(
    job_title: str,
    job_description: str,
    required_skills: list[str],
) -> dict:
    """Return default questions when AI generation fails."""
    all_questions = []
    idx = 1

    # Add technical questions based on required skills
    for skill in required_skills[:3]:
        all_questions.append({
            "id": idx,
            "question": f"Describe your experience with {skill}. What projects have you used it on?",
            "category": "technical",
            "difficulty": "medium",
            "skill_area": skill.lower().replace(" ", "_"),
            "follow_up": f"What are some limitations or trade-offs you've encountered with {skill}?",
            "evaluation_criteria": f"Depth of {skill} knowledge and practical application.",
            "time_allocation_minutes": 5,
        })
        idx += 1

    # Add standard behavioral + culture questions
    for cat, q_list in FALLBACK_QUESTIONS.items():
        for q in q_list:
            all_questions.append({**q, "id": idx})
            idx += 1

    structure = _build_interview_structure(all_questions)

    return {
        "job_title": job_title,
        "total_questions": len(all_questions),
        "questions": all_questions,
        "interview_structure": structure,
        "generated_by_ai": False,
    }
