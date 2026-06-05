import logging
import asyncio
from datetime import datetime, timezone
from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.recruitment import Application, AIEvaluation, Candidate, ApplicationStage
from app.ai.engines.resume_intelligence import analyze_resume
from app.ai.engines.candidate_match import match_candidate_to_job
from app.ai.engines.candidate_evaluation import evaluate_candidate
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def _async_process_resume(application_id: str, resume_url: str):
    async with AsyncSessionLocal() as db:
        try:
            # 1. Fetch application details, candidate and job posting
            stmt = (
                select(Application)
                .where(Application.id == application_id)
            )
            res = await db.execute(stmt)
            application = res.scalar_one_or_none()
            if not application:
                logger.error(f"Application {application_id} not found.")
                return

            candidate = application.candidate
            job_posting = application.job_posting

            # 2. Extract text and analyze resume using resume_intelligence
            logger.info(f"Running resume intelligence on {resume_url}")
            analysis = await analyze_resume(resume_url)

            # Update candidate's fields if empty and we got them from resume
            candidate.resume_text = analysis.get("raw_text")
            cand_info = analysis.get("candidate", {})
            if cand_info:
                if not candidate.first_name and cand_info.get("first_name"):
                    candidate.first_name = cand_info.get("first_name")
                if not candidate.last_name and cand_info.get("last_name"):
                    candidate.last_name = cand_info.get("last_name")
                if not candidate.phone and cand_info.get("phone"):
                    candidate.phone = cand_info.get("phone")
                if not candidate.linkedin_url and cand_info.get("linkedin_url"):
                    candidate.linkedin_url = cand_info.get("linkedin_url")

            # 3. Match candidate to job specs
            required_skills = [
                s.strip()
                for s in (job_posting.requirements or "").split(",")
                if s.strip()
            ]
            match_res = await match_candidate_to_job(
                candidate_skills=analysis.get("skills", []),
                candidate_experience_years=analysis.get("total_experience_years", 0.0),
                resume_text=analysis.get("raw_text", ""),
                job_title=job_posting.title,
                job_description=job_posting.description,
                job_requirements=job_posting.requirements or "",
                required_skills=required_skills,
                experience_min=job_posting.experience_min or 0.0,
                experience_max=job_posting.experience_max or 10.0,
            )

            # 4. Deep AI Candidate Evaluation
            eval_res = await evaluate_candidate(
                candidate_name=f"{candidate.first_name} {candidate.last_name}",
                candidate_skills=analysis.get("skills", []),
                candidate_experience_years=analysis.get("total_experience_years", 0.0),
                education_summary=", ".join([
                    f"{e.get('degree', '')} from {e.get('institution', '')}"
                    for e in analysis.get("education", [])
                ]),
                resume_summary=analysis.get("summary", ""),
                job_title=job_posting.title,
                job_description=job_posting.description,
                required_skills=required_skills,
                experience_min=job_posting.experience_min or 0.0,
                experience_max=job_posting.experience_max or 10.0,
                match_score=match_res.get("overall_match_score", 50.0),
                matched_skills=match_res.get("matched_skills", []),
                missing_skills=match_res.get("missing_skills", []),
            )

            # 5. Create or update AIEvaluation record
            ai_eval = application.ai_evaluation
            if not ai_eval:
                ai_eval = AIEvaluation(
                    application_id=application.id,
                )
                db.add(ai_eval)

            ai_eval.fit_score = eval_res.get("fit_score")
            ai_eval.skill_match_score = eval_res.get("skill_match_score")
            ai_eval.experience_score = eval_res.get("experience_score")
            ai_eval.overall_score = eval_res.get("overall_score")
            ai_eval.strengths = eval_res.get("strengths")
            ai_eval.weaknesses = eval_res.get("weaknesses")
            ai_eval.ai_summary = eval_res.get("ai_summary")
            ai_eval.recommendation = eval_res.get("recommendation")
            ai_eval.confidence = eval_res.get("confidence")

            # Transition application stage to "ai_screening"
            application.stage = ApplicationStage.ai_screening
            now_str = datetime.now(timezone.utc).isoformat()
            history = list(application.stage_history or [])
            history.append({
                "stage": "ai_screening",
                "timestamp": now_str,
                "notes": "AI Screening evaluation completed"
            })
            application.stage_history = history

            await db.commit()
            logger.info(f"Resume processing and AI evaluation completed for application {application_id}")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error in _async_process_resume: {e}")
            raise


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_resume(self, application_id: str, resume_url: str):
    """Process uploaded resume: extract text, run AI evaluation."""
    logger.info(f"Processing resume for application {application_id}")
    try:
        asyncio.run(_async_process_resume(application_id, resume_url))
        return {"status": "completed", "application_id": application_id}
    except Exception as exc:
        logger.error(f"Resume processing failed: {exc}")
        raise self.retry(exc=exc)
