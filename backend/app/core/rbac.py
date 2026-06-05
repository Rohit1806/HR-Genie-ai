from functools import wraps
from typing import List
from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.models.auth import User, UserRole
import logging

logger = logging.getLogger(__name__)


def require_roles(*roles: UserRole):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin-only")
        async def admin_route(
            current_user: User = Depends(require_roles(UserRole.ADMIN))
        ):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            logger.warning(
                f"Access denied: user {current_user.id} with role {current_user.role} "
                f"attempted to access route requiring {roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of: {[r.value for r in roles]}"
            )
        return current_user
    return role_checker


# Convenience dependencies
require_admin = require_roles(UserRole.ADMIN)
require_hr = require_roles(UserRole.ADMIN, UserRole.HR_RECRUITER)
require_manager = require_roles(UserRole.ADMIN, UserRole.SENIOR_MANAGER)
require_hr_or_manager = require_roles(
    UserRole.ADMIN, UserRole.HR_RECRUITER, UserRole.SENIOR_MANAGER
)
require_any_role = require_roles(
    UserRole.ADMIN, UserRole.SENIOR_MANAGER, UserRole.HR_RECRUITER, UserRole.EMPLOYEE
)
