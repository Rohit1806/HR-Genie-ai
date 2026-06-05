"""
Recruitment service for HRGenie AI.
Full recruitment pipeline: job postings, applications, stage transitions,
candidate ranking, and AI evaluation hooks.
"""

import os
import uuid as _uuid
from datetime import datetime, timezone, date
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.recruitment import (
    JobPosting,
    Candidate,
    Application,
    AIEvaluation,
    VoiceScreening,
    InterviewQuestions,
    Offer,
    JobStatus,
    ApplicationStage,
    OfferStatus,
)
from app.schemas.recruitment import (
    JobPostingCreateSchema,
    JobPostingUpdateSchema,
    JobPostingSummarySchema,
    JobPostingDetailSchema,
    CandidateCreateSchema,
    ApplicationCreateSchema,
    ApplicationStageUpdateSchema,
    ApplicationSummarySchema,
    ApplicationDetailSchema,
    OfferCreateSchema,
    OfferSchema,
)

class RecruitmentServiceError(Exception):
    """Custom exception for recruitment service errors."""
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


# Stage transitions mapping
VALID_STAGES = [stage.value for stage in ApplicationStage]

STAGE_TRANSITIONS = {
    "applied": ["ai_screening", "shortlisted", "rejected"],
    "ai_screening": ["shortlisted", "interview", "rejected"],
    "shortlisted": ["interview", "rejected"],
    "interview": ["technical", "hr_round", "offered", "rejected"],
    "technical": ["hr_round", "offered", "rejected"],
    "hr_round": ["offered", "rejected"],
    "offered": ["hired", "rejected"],
    "hired": [],
    "rejected": [],
}


async def list_job_postings(
    company_id: UUID,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = None,
) -> dict:
    """List job postings with optional status filter and pagination."""
    query = select(JobPosting).where(
        JobPosting.company_id == company_id,
        JobPosting.deleted_at.is_(None),
    )
    if status:
        query = query.where(JobPosting.status == JobStatus(status))

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(JobPosting.created_at.desc())
    query = query.options(selectinload(JobPosting.department))
    result = await db.execute(query)
    postings = result.scalars().all()

    items = []
    for jp in postings:
        # Get application count
        app_count_q = select(func.count()).select_from(Application).where(
            Application.job_posting_id == jp.id,
            Application.deleted_at.is_(None),
        )
        app_count = (await db.execute(app_count_q)).scalar() or 0

        items.append(
            JobPostingSummarySchema(
                id=jp.id,
                title=jp.title,
                department_name=jp.department.name if jp.department else None,
                employment_type=jp.employment_type,
                location=jp.location,
                salary_min=float(jp.salary_min) if jp.salary_min else None,
                salary_max=float(jp.salary_max) if jp.salary_max else None,
                status=jp.status.value if hasattr(jp.status, 'value') else jp.status,
                openings_count=jp.openings_count,
                applications_count=app_count,
                created_at=jp.created_at,
            )
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


async def create_job_posting(
    data: JobPostingCreateSchema,
    company_id: UUID,
    user_id: UUID,
    db: AsyncSession,
) -> dict:
    """Create a new job posting."""
    posting = JobPosting(
        company_id=company_id,
        title=data.title,
        description=data.description,
        department_id=data.department_id,
        location=data.location,
        employment_type=data.employment_type,
        experience_min=data.experience_min,
        experience_max=data.experience_max,
        salary_min=data.salary_min,
        salary_max=data.salary_max,
        openings_count=data.openings_count,
        status=JobStatus.open,
        posted_by=user_id,
    )
    db.add(posting)
    await db.flush()
    await db.refresh(posting)

    return {
        "id": str(posting.id),
        "title": posting.title,
        "status": posting.status.value if hasattr(posting.status, 'value') else posting.status,
        "created_at": posting.created_at.isoformat() if posting.created_at else None,
    }


async def get_job_posting_detail(
    id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> JobPostingDetailSchema | None:
    """Get job posting detail."""
    stmt = (
        select(JobPosting)
        .where(
            JobPosting.id == id,
            JobPosting.company_id == company_id,
            JobPosting.deleted_at.is_(None),
        )
        .options(
            selectinload(JobPosting.department),
            selectinload(JobPosting.poster),
        )
    )
    result = await db.execute(stmt)
    jp = result.scalar_one_or_none()

    if not jp:
        return None

    return JobPostingDetailSchema(
        id=jp.id,
        title=jp.title,
        department_id=jp.department_id,
        department_name=jp.department.name if jp.department else None,
        employment_type=jp.employment_type,
        location=jp.location,
        salary_min=float(jp.salary_min) if jp.salary_min else None,
        salary_max=float(jp.salary_max) if jp.salary_max else None,
        description=jp.description,
        requirements=jp.requirements,
        experience_min=jp.experience_min,
        experience_max=jp.experience_max,
        status=jp.status.value if hasattr(jp.status, 'value') else jp.status,
        openings_count=jp.openings_count,
        deadline=jp.deadline,
        posted_by_name=jp.poster.full_name if jp.poster else None,
        created_at=jp.created_at,
    )


async def update_job_posting(
    id: UUID,
    data: JobPostingUpdateSchema,
    company_id: UUID,
    db: AsyncSession,
) -> dict | None:
    """Update a job posting."""
    stmt = select(JobPosting).where(
        JobPosting.id == id,
        JobPosting.company_id == company_id,
        JobPosting.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    jp = result.scalar_one_or_none()

    if not jp:
        return None

    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        if field == "status" and isinstance(value, str):
            value = JobStatus(value)
        setattr(jp, field, value)

    jp.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(jp)

    return {
        "id": str(jp.id),
        "title": jp.title,
        "status": jp.status.value if hasattr(jp.status, 'value') else jp.status,
        "updated_at": jp.updated_at.isoformat() if jp.updated_at else None,
    }


async def submit_application(
    data: ApplicationCreateSchema,
    resume_content: bytes | None,
    resume_filename: str | None,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """
    Submit a job application.
    """
    # Validate job is open
    jp_stmt = select(JobPosting).where(
        JobPosting.id == data.job_posting_id,
        JobPosting.company_id == company_id,
        JobPosting.deleted_at.is_(None),
    )
    jp_result = await db.execute(jp_stmt)
    jp = jp_result.scalar_one_or_none()

    if not jp:
        raise RecruitmentServiceError("Job posting not found.", status_code=404)
    if jp.status != JobStatus.open:
        raise RecruitmentServiceError("Job posting is not open for applications.", status_code=400)

    # Check duplicate application (Join candidate to search by email)
    dup_stmt = (
        select(Application)
        .join(Application.candidate)
        .where(
            Application.job_posting_id == data.job_posting_id,
            Candidate.email == data.email,
            Application.deleted_at.is_(None),
        )
    )
    dup_result = await db.execute(dup_stmt)
    if dup_result.scalar_one_or_none():
        raise RecruitmentServiceError("Application already submitted for this job.", status_code=409)

    # Upsert candidate
    cand_stmt = select(Candidate).where(
        Candidate.email == data.email,
        Candidate.company_id == company_id,
    )
    cand_result = await db.execute(cand_stmt)
    candidate = cand_result.scalar_one_or_none()

    if not candidate:
        candidate = Candidate(
            company_id=company_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
        )
        db.add(candidate)
        await db.flush()

    # Save resume
    resume_url = None
    if resume_content and resume_filename:
        upload_dir = os.path.join(settings.UPLOAD_DIR, "resumes", str(candidate.id))
        os.makedirs(upload_dir, exist_ok=True)
        unique_name = f"{_uuid.uuid4().hex}_{resume_filename}"
        file_path = os.path.join(upload_dir, unique_name)
        with open(file_path, "wb") as f:
            f.write(resume_content)
        resume_url = file_path
        candidate.resume_url = file_path

    # Create application
    now = datetime.now(timezone.utc)
    application = Application(
        job_posting_id=data.job_posting_id,
        candidate_id=candidate.id,
        stage=ApplicationStage.applied,
        stage_history=[{"stage": "applied", "timestamp": now.isoformat(), "notes": "Application submitted"}],
        applied_at=now,
        source=data.source,
        current_ctc=data.current_ctc,
        expected_ctc=data.expected_ctc,
        notice_period_days=data.notice_period_days,
    )
    db.add(application)
    await db.flush()
    await db.refresh(application)

    if resume_url:
        await db.commit()
        from app.workers.tasks.resume_processing import process_resume
        process_resume.delay(str(application.id), resume_url)

    return {
        "id": str(application.id),
        "job_posting_id": str(application.job_posting_id),
        "candidate_name": f"{candidate.first_name} {candidate.last_name}",
        "stage": application.stage.value if hasattr(application.stage, 'value') else application.stage,
        "applied_at": application.applied_at.isoformat() if application.applied_at else None,
    }


async def list_applications(
    company_id: UUID,
    job_posting_id: UUID | None = None,
    stage: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = None,
) -> dict:
    """List applications with filters."""
    query = (
        select(Application)
        .join(Application.job_posting)
        .join(Application.candidate)
        .where(
            JobPosting.company_id == company_id,
            Application.deleted_at.is_(None),
        )
    )
    if job_posting_id:
        query = query.where(Application.job_posting_id == job_posting_id)
    if stage:
        query = query.where(Application.stage == ApplicationStage(stage))

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Application.applied_at.desc())
    query = query.options(
        selectinload(Application.job_posting),
        selectinload(Application.candidate),
        selectinload(Application.ai_evaluation),
    )
    result = await db.execute(query)
    apps = result.scalars().all()

    items = []
    for a in apps:
        fit_score = a.ai_evaluation.overall_score if a.ai_evaluation else None
        recommendation = a.ai_evaluation.recommendation if a.ai_evaluation else None
        
        items.append(
            ApplicationSummarySchema(
                id=a.id,
                job_posting_id=a.job_posting_id,
                job_title=a.job_posting.title,
                candidate_id=a.candidate_id,
                candidate_name=f"{a.candidate.first_name} {a.candidate.last_name}",
                stage=a.stage.value if hasattr(a.stage, 'value') else a.stage,
                applied_at=a.applied_at,
                overall_score=fit_score,
                recommendation=recommendation,
            )
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


async def get_application_detail(
    id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> ApplicationDetailSchema | None:
    """Get application detail with AI evaluation."""
    stmt = (
        select(Application)
        .join(Application.job_posting)
        .where(
            Application.id == id,
            JobPosting.company_id == company_id,
            Application.deleted_at.is_(None),
        )
        .options(
            selectinload(Application.job_posting),
            selectinload(Application.candidate),
            selectinload(Application.ai_evaluation),
        )
    )
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        return None

    from app.schemas.recruitment import CandidateSchema, AIEvaluationSchema
    candidate_schema = CandidateSchema(
        id=app.candidate.id,
        first_name=app.candidate.first_name,
        last_name=app.candidate.last_name,
        email=app.candidate.email,
        phone=app.candidate.phone,
        linkedin_url=app.candidate.linkedin_url,
        resume_url=app.candidate.resume_url,
    )

    ai_eval_schema = None
    if app.ai_evaluation:
        ae = app.ai_evaluation
        ai_eval_schema = AIEvaluationSchema(
            id=ae.id,
            application_id=ae.application_id,
            fit_score=ae.fit_score,
            skill_match_score=ae.skill_match_score,
            experience_score=ae.experience_score,
            overall_score=ae.overall_score,
            strengths=ae.strengths,
            weaknesses=ae.weaknesses,
            ai_summary=ae.ai_summary,
            recommendation=ae.recommendation,
            confidence=ae.confidence,
            human_override=ae.human_override,
            override_notes=ae.override_notes,
        )

    return ApplicationDetailSchema(
        id=app.id,
        job_posting_id=app.job_posting_id,
        job_title=app.job_posting.title,
        candidate=candidate_schema,
        stage=app.stage.value if hasattr(app.stage, 'value') else app.stage,
        applied_at=app.applied_at,
        source=app.source,
        rejection_reason=app.rejection_reason,
        current_ctc=float(app.current_ctc) if app.current_ctc else None,
        expected_ctc=float(app.expected_ctc) if app.expected_ctc else None,
        notice_period_days=app.notice_period_days,
        stage_history=app.stage_history or [],
        ai_evaluation=ai_eval_schema,
    )


async def update_stage(
    id: UUID,
    new_stage: str,
    rejection_reason: str | None,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """
    Transition application to a new stage.
    """
    stmt = (
        select(Application)
        .join(Application.job_posting)
        .where(
            Application.id == id,
            JobPosting.company_id == company_id,
            Application.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        raise RecruitmentServiceError("Application not found.", status_code=404)

    current_stage_str = app.stage.value if hasattr(app.stage, 'value') else app.stage
    
    # Validate transition
    allowed = STAGE_TRANSITIONS.get(current_stage_str, [])
    if new_stage not in allowed and new_stage != "rejected":
        # Allow transition to rejected from anywhere
        raise RecruitmentServiceError(
            f"Cannot transition from '{current_stage_str}' to '{new_stage}'. Allowed: {allowed}",
            status_code=400
        )

    now = datetime.now(timezone.utc)
    history_entry = {
        "stage": new_stage,
        "timestamp": now.isoformat(),
        "notes": rejection_reason if new_stage == "rejected" else None,
    }

    stage_history = list(app.stage_history or [])
    stage_history.append(history_entry)
    app.stage_history = stage_history
    app.stage = ApplicationStage(new_stage)

    if new_stage == "rejected" and rejection_reason:
        app.rejection_reason = rejection_reason

    app.updated_at = now
    await db.flush()
    await db.refresh(app)

    return {
        "id": str(app.id),
        "stage": app.stage.value if hasattr(app.stage, 'value') else app.stage,
        "stage_history": app.stage_history,
    }


async def get_ranked_candidates(
    job_posting_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Get candidates ranked by AI overall_score descending."""
    stmt = (
        select(Application)
        .join(Application.job_posting)
        .join(Application.ai_evaluation)
        .where(
            Application.job_posting_id == job_posting_id,
            JobPosting.company_id == company_id,
            Application.deleted_at.is_(None),
            AIEvaluation.overall_score.isnot(None),
        )
        .options(selectinload(Application.candidate), selectinload(Application.ai_evaluation))
        .order_by(desc(AIEvaluation.overall_score))
    )
    result = await db.execute(stmt)
    apps = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "candidate_name": f"{a.candidate.first_name} {a.candidate.last_name}",
            "candidate_email": a.candidate.email,
            "stage": a.stage.value if hasattr(a.stage, 'value') else a.stage,
            "overall_score": a.ai_evaluation.overall_score if a.ai_evaluation else None,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None,
        }
        for a in apps
    ]


async def get_interview_questions(
    application_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """
    Get existing interview questions for the job posting associated with this application.
    """
    stmt = (
        select(Application)
        .join(Application.job_posting)
        .where(
            Application.id == application_id,
            JobPosting.company_id == company_id,
            Application.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()
    if not app:
        raise RecruitmentServiceError("Application not found.", status_code=404)

    # Fetch interview questions for the job posting
    stmt_q = select(InterviewQuestions).where(
        InterviewQuestions.job_posting_id == app.job_posting_id,
        InterviewQuestions.deleted_at.is_(None),
    )
    result_q = await db.execute(stmt_q)
    iq = result_q.scalar_one_or_none()

    if not iq or not iq.questions:
        # Fallback to generate on the fly
        return await generate_interview_questions(
            application_id=application_id,
            focus_areas=None,
            company_id=company_id,
            db=db,
        )

    return iq.questions


async def generate_interview_questions(
    application_id: UUID,
    focus_areas: list[str] | None,
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """
    Generate tailored interview questions using AI (or fallback default list).
    """
    stmt = (
        select(Application)
        .join(Application.job_posting)
        .options(selectinload(Application.job_posting))
        .where(
            Application.id == application_id,
            JobPosting.company_id == company_id,
            Application.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()
    if not app:
        raise RecruitmentServiceError("Application not found.", status_code=404)

    job_title = app.job_posting.title
    
    # Generate some high-quality default questions
    default_questions = [
        {
            "question": f"Can you walk us through a challenging project you worked on as a {job_title} and how you handled it?",
            "category": "behavioral",
            "difficulty": "medium",
            "expected_answer_points": [
                "STAR method (Situation, Task, Action, Result)",
                "Clarity of thought and explanation",
                "Technical contributions and decision-making details",
                "Collaboration and communication skills"
            ]
        },
        {
            "question": f"What are the core technical design principles you follow when building systems/solutions in your recent projects?",
            "category": "technical",
            "difficulty": "hard",
            "expected_answer_points": [
                "Scalability, readability, and reliability principles",
                "Clean code and robust design pattern examples",
                "Testing and validation strategies",
                "Trade-offs consideration"
            ]
        },
        {
            "question": "If you disagree with a product requirement or an engineering decision made by a peer, how do you resolve it?",
            "category": "situational",
            "difficulty": "easy",
            "expected_answer_points": [
                "Active listening and empathy",
                "Data-backed reasoning",
                "Constructive debate and compromise",
                "Commitment to final team decision"
            ]
        },
        {
            "question": f"Why do you want to join our company as a {job_title}, and how do your long-term goals align with this role?",
            "category": "culture_fit",
            "difficulty": "easy",
            "expected_answer_points": [
                "Understanding of our core mission and values",
                "Genuine interest in the role and tech stack",
                "Growth mindset and motivation for impact",
                "Professional and cultural value-add potential"
            ]
        }
    ]

    # Try calling Gemini to generate questions if key is configured
    questions = default_questions
    if settings.GEMINI_API_KEY:
        try:
            import logging
            logger = logging.getLogger(__name__)
            from app.ai.gemini_client import call_gemini_json
            from app.ai.prompts.interview_questions import INTERVIEW_QUESTIONS_PROMPT
            
            prompt = INTERVIEW_QUESTIONS_PROMPT.format(
                job_title=job_title,
                requirements=", ".join(app.job_posting.requirements or []),
                focus_areas=", ".join(focus_areas) if focus_areas else "General technical and behavioral fitness"
            )
            ai_res = await call_gemini_json(prompt)
            if isinstance(ai_res, list) and len(ai_res) > 0:
                questions = ai_res
            elif isinstance(ai_res, dict) and "questions" in ai_res:
                questions = ai_res["questions"]
        except Exception as e:
            logger.error(f"Failed to generate questions using Gemini: {e}. Falling back to default list.")

    # Save to database (upsert InterviewQuestions)
    stmt_iq = select(InterviewQuestions).where(
        InterviewQuestions.job_posting_id == app.job_posting_id,
        InterviewQuestions.deleted_at.is_(None)
    )
    res_iq = await db.execute(stmt_iq)
    iq_obj = res_iq.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    if not iq_obj:
        iq_obj = InterviewQuestions(
            id=_uuid.uuid4(),
            job_posting_id=app.job_posting_id,
            questions=questions,
            generated_by_ai=True,
            created_at=now,
            updated_at=now,
        )
        db.add(iq_obj)
    else:
        iq_obj.questions = questions
        iq_obj.updated_at = now
    
    await db.flush()
    return questions


async def process_voice_screening_evaluation(
    application_id: UUID,
    audio_relative_path: str,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Process voice screening audio recording and save evaluation results."""
    # 1. Fetch application, candidate and job posting
    stmt = (
        select(Application)
        .join(Application.job_posting)
        .where(
            Application.id == application_id,
            JobPosting.company_id == company_id,
            Application.deleted_at.is_(None),
        )
        .options(
            selectinload(Application.job_posting),
            selectinload(Application.candidate),
        )
    )
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()
    if not app:
        raise RecruitmentServiceError("Application not found.", status_code=404)

    # Resolve disk path
    clean_path = audio_relative_path.replace("/uploads/", "")
    disk_path = os.path.join(settings.UPLOAD_DIR, clean_path)

    # 2. Retrieve questions asked
    q_stmt = select(InterviewQuestions).where(
        InterviewQuestions.job_posting_id == app.job_posting_id,
        InterviewQuestions.deleted_at.is_(None),
    )
    q_res = await db.execute(q_stmt)
    iq_obj = q_res.scalar_one_or_none()
    questions_list = []
    if iq_obj and iq_obj.questions:
        questions_list = [q.get("question") for q in iq_obj.questions if q.get("question")]

    # 3. Call process_voice_screening engine
    from app.ai.engines.voice_screening import process_voice_screening
    evaluation = await process_voice_screening(
        audio_file_path=disk_path,
        job_title=app.job_posting.title,
        questions_asked=questions_list or None,
        candidate_name=f"{app.candidate.first_name} {app.candidate.last_name}",
    )

    # 4. Save VoiceScreening record
    vs = VoiceScreening(
        application_id=app.id,
        audio_url=audio_relative_path,
        transcript=evaluation.get("transcript"),
        ai_evaluation={
            "speech_metrics": evaluation.get("speech_metrics"),
            "communication_score": evaluation.get("communication_score"),
            "content_evaluation": evaluation.get("content_evaluation"),
            "strengths": evaluation.get("strengths"),
            "areas_for_improvement": evaluation.get("areas_for_improvement"),
            "key_highlights": evaluation.get("key_highlights"),
            "ai_summary": evaluation.get("ai_summary"),
        },
        overall_voice_score=evaluation.get("overall_voice_score"),
        recommendation=evaluation.get("recommendation"),
    )
    db.add(vs)
    await db.flush()

    return {
        "id": str(vs.id),
        "application_id": str(vs.application_id),
        "audio_url": vs.audio_url,
        "transcript": vs.transcript,
        "overall_voice_score": vs.overall_voice_score,
        "recommendation": vs.recommendation,
        "ai_evaluation": vs.ai_evaluation,
    }


async def get_voice_screenings(
    application_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """Retrieve all voice screenings recorded for an application."""
    # Verify application
    stmt = (
        select(Application)
        .join(Application.job_posting)
        .where(
            Application.id == application_id,
            JobPosting.company_id == company_id,
            Application.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise RecruitmentServiceError("Application not found.", status_code=404)

    vs_stmt = select(VoiceScreening).where(VoiceScreening.application_id == application_id)
    vs_result = await db.execute(vs_stmt)
    screenings = vs_result.scalars().all()

    return [
        {
            "id": str(s.id),
            "application_id": str(s.application_id),
            "audio_url": s.audio_url,
            "transcript": s.transcript,
            "overall_voice_score": s.overall_voice_score,
            "recommendation": s.recommendation,
            "ai_evaluation": s.ai_evaluation,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in screenings
    ]
