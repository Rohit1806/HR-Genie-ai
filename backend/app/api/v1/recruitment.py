"""
Recruitment API router for HRGenie AI.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac import require_hr
from app.models.auth import User
from app.schemas.recruitment import (
    JobPostingCreateSchema,
    JobPostingUpdateSchema,
    JobPostingSummarySchema,
    JobPostingDetailSchema,
    ApplicationCreateSchema,
    ApplicationStageUpdateSchema,
    ApplicationSummarySchema,
    ApplicationDetailSchema,
)
from app.services import recruitment_service
from app.core.exceptions import ValidationError, NotFoundError
from app.utils.file_handler import validate_file, save_file

router = APIRouter()


@router.get("/jobs", response_model=dict)
async def list_job_postings(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all job postings in the company.
    """
    return await recruitment_service.list_job_postings(
        company_id=current_user.company_id,
        status=status,
        page=page,
        page_size=page_size,
        db=db,
    )


@router.post("/jobs", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_hr)])
async def create_job_posting(
    data: JobPostingCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new job posting. (HR/Admin only)
    """
    return await recruitment_service.create_job_posting(
        data=data,
        company_id=current_user.company_id,
        user_id=current_user.id,
        db=db,
    )


@router.get("/jobs/{id}", response_model=JobPostingDetailSchema)
async def get_job_posting_detail(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get details of a job posting.
    """
    posting = await recruitment_service.get_job_posting_detail(
        id=id,
        company_id=current_user.company_id,
        db=db,
    )
    if not posting:
        raise NotFoundError("Job posting not found.")
    return posting


@router.patch("/jobs/{id}", response_model=dict, dependencies=[Depends(require_hr)])
async def update_job_posting(
    id: UUID,
    data: JobPostingUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update details or status of a job posting. (HR/Admin only)
    """
    res = await recruitment_service.update_job_posting(
        id=id,
        data=data,
        company_id=current_user.company_id,
        db=db,
    )
    if not res:
        raise NotFoundError("Job posting not found.")
    return res


@router.post("/applications", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_application(
    job_posting_id: UUID = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    current_ctc: Optional[float] = Form(None),
    expected_ctc: Optional[float] = Form(None),
    notice_period_days: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a job application along with a resume file.
    """
    from app.schemas.recruitment import EmailStr
    app_data = ApplicationCreateSchema(
        job_posting_id=job_posting_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        linkedin_url=linkedin_url,
        source=source,
        current_ctc=current_ctc,
        expected_ctc=expected_ctc,
        notice_period_days=notice_period_days,
    )
    
    resume_content = None
    resume_filename = None
    if file:
        validate_file(file, "resume")
        resume_content = await file.read()
        resume_filename = file.filename
        
    return await recruitment_service.submit_application(
        data=app_data,
        resume_content=resume_content,
        resume_filename=resume_filename,
        company_id=current_user.company_id,
        db=db,
    )


@router.get("/applications", response_model=dict)
async def list_applications(
    job_posting_id: Optional[UUID] = None,
    stage: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List candidate applications.
    """
    return await recruitment_service.list_applications(
        company_id=current_user.company_id,
        job_posting_id=job_posting_id,
        stage=stage,
        page=page,
        page_size=page_size,
        db=db,
    )


@router.get("/applications/{id}", response_model=ApplicationDetailSchema)
async def get_application_detail(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed profile of an application, including candidate info and AI evaluation.
    """
    app_detail = await recruitment_service.get_application_detail(
        id=id,
        company_id=current_user.company_id,
        db=db,
    )
    if not app_detail:
        raise NotFoundError("Application not found.")
    return app_detail


@router.patch("/applications/{id}/stage", response_model=dict, dependencies=[Depends(require_hr)])
async def update_application_stage(
    id: UUID,
    data: ApplicationStageUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Transition application stage. (HR/Admin only)
    """
    try:
        return await recruitment_service.update_stage(
            id=id,
            new_stage=data.stage,
            rejection_reason=data.rejection_reason,
            company_id=current_user.company_id,
            db=db,
        )
    except ValueError as e:
        raise ValidationError(str(e))


@router.get("/jobs/{id}/ranked-candidates", response_model=list[dict], dependencies=[Depends(require_hr)])
async def get_ranked_candidates(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get candidate applications ranked by AI overall evaluation score. (HR/Admin only)
    """
    return await recruitment_service.get_ranked_candidates(
        job_posting_id=id,
        company_id=current_user.company_id,
        db=db,
    )


@router.get("/applications/{id}/interview-questions", response_model=list[dict], dependencies=[Depends(require_hr)])
async def get_interview_questions(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get interview questions associated with this application's job posting.
    """
    return await recruitment_service.get_interview_questions(
        application_id=id,
        company_id=current_user.company_id,
        db=db,
    )


@router.post("/applications/{id}/interview-questions/generate", response_model=list[dict], dependencies=[Depends(require_hr)])
async def generate_interview_questions(
    id: UUID,
    body: dict = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Regenerate interview questions tailored to the job posting and optional focus areas.
    """
    focus_areas = body.get("focus_areas") if body else None
    return await recruitment_service.generate_interview_questions(
        application_id=id,
        focus_areas=focus_areas,
        company_id=current_user.company_id,
        db=db,
    )


@router.post("/applications/{id}/voice-screening", response_model=dict, dependencies=[Depends(require_hr)])
async def upload_voice_screening(
    id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an audio recording of candidate voice screening and perform AI evaluation.
    """
    # 1. Validate file format is audio
    validate_file(file, "audio")

    # 2. Save the file locally
    audio_path = await save_file(file, "voice_screenings")

    # 3. Call recruitment service to evaluate and store in DB
    return await recruitment_service.process_voice_screening_evaluation(
        application_id=id,
        audio_relative_path=audio_path,
        company_id=current_user.company_id,
        db=db,
    )


@router.get("/applications/{id}/voice-screenings", response_model=list[dict], dependencies=[Depends(require_hr)])
async def get_voice_screenings(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all voice screenings for an application.
    """
    return await recruitment_service.get_voice_screenings(
        application_id=id,
        company_id=current_user.company_id,
        db=db,
    )
