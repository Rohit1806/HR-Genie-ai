"""
Admin API router for HRGenie AI.
"""

from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.core.rbac import require_admin
from app.models.auth import User

router = APIRouter()


@router.get("/health-check", dependencies=[Depends(require_admin)])
async def admin_health_check(current_user: User = Depends(get_current_user)):
    """
    Endpoint for admins to verify backend and DB status.
    """
    return {"status": "ok", "role": current_user.role}
