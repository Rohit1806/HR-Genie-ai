"""
AI API router for HRGenie AI.
Interfaces with the Gemini AI engines and SentenceTransformer embeddings.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac import require_hr
from app.models.auth import User
from app.schemas.auth import MessageResponse

# Lazy load AI engines since they are stubs / placeholders
from app.ai.engines import (
    hr_copilot,
    resume_intelligence,
    attrition_predictor,
    promotion_recommender,
)

router = APIRouter()


@router.post("/copilot/chat")
async def copilot_chat(
    message: str = Form(...),
    session_id: str | None = Form(None),
    current_user: User = Depends(get_current_user),
):
    """
    Interact with the HR Copilot.
    """
    response = await hr_copilot.chat(
        message=message,
        session_id=session_id,
        user_id=current_user.id,
        company_id=current_user.company_id,
    )
    return response


@router.post("/copilot/action")
async def copilot_action(
    action: str = Form(...),
    params: str | None = Form(None),
    current_user: User = Depends(get_current_user),
):
    """
    Execute a quick action or command via the HR Copilot (e.g. drafting email).
    """
    import json
    parsed_params = {}
    if params:
        try:
            parsed_params = json.loads(params)
        except Exception:
            pass
            
    response = await hr_copilot.execute_action(
        action=action,
        params=parsed_params,
        user_id=current_user.id,
        company_id=current_user.company_id,
    )
    return response


@router.get("/attrition-risk/{employee_id}", dependencies=[Depends(require_hr)])
async def get_attrition_risk(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate and predict the attrition risk of a specific employee.
    """
    risk_data = await attrition_predictor.predict_attrition(
        employee_id=employee_id,
        db=db,
    )
    return risk_data


@router.get("/promotion-score/{employee_id}", dependencies=[Depends(require_hr)])
async def get_promotion_score(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate AI readiness and recommendation scores for employee promotion.
    """
    promotion_data = await promotion_recommender.recommend_promotion(
        employee_id=employee_id,
        db=db,
    )
    return promotion_data


@router.post("/resume/parse", dependencies=[Depends(require_hr)])
async def parse_resume(
    file: UploadFile = File(...),
):
    """
    Extract entity details (experience, skills, contact) from an uploaded resume.
    """
    contents = await file.read()
    filename = file.filename or "resume.pdf"
    
    parsed_data = await resume_intelligence.parse_resume(
        file_bytes=contents,
        filename=filename,
    )
    return parsed_data
