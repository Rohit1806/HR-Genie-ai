"""
Authentication service for HRGenie AI.
Handles login, token refresh/rotation, logout, and password reset flows.
JWT: 15-min access tokens, 7-day refresh stored hashed in DB, HttpOnly cookie.
Lockout: 5 failed attempts → 15-minute Redis-backed lock.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    generate_reset_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.config import settings

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60  # 15 minutes
RESET_TOKEN_TTL = timedelta(hours=1)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenRefreshResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserContext,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_lockout_key(email: str) -> str:
    return f"lockout:{email}"


async def _check_lockout(email: str, redis: aioredis.Redis) -> None:
    """Raise if user is currently locked out."""
    key = await _get_lockout_key(email)
    attempts = await redis.get(key)
    if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
        ttl = await redis.ttl(key)
        raise AuthError(
            f"Account locked due to too many failed attempts. Try again in {ttl} seconds.",
            status_code=429,
        )


async def _increment_fail(email: str, redis: aioredis.Redis) -> int:
    """Increment failed login counter. Returns new count."""
    key = await _get_lockout_key(email)
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, LOCKOUT_SECONDS)
    results = await pipe.execute()
    return int(results[0])


async def _clear_lockout(email: str, redis: aioredis.Redis) -> None:
    key = await _get_lockout_key(email)
    await redis.delete(key)


class AuthError(Exception):
    """Custom exception for authentication errors."""

    def __init__(self, detail: str, status_code: int = 401):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def login(
    email: str,
    password: str,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> tuple[LoginResponse, str]:
    """
    Authenticate user, return (LoginResponse, raw_refresh_token).
    The caller sets the refresh token in an HttpOnly cookie.
    """
    # Late import to avoid circular dependency with models
    from app.models.auth import User, RefreshToken

    # Check lockout
    await _check_lockout(email, redis)

    # Find user
    stmt = select(User).where(
        User.email == email,
        User.is_active.is_(True),
        User.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        count = await _increment_fail(email, redis)
        remaining = MAX_LOGIN_ATTEMPTS - count
        if remaining <= 0:
            raise AuthError(
                "Account locked due to too many failed attempts. Try again in 15 minutes.",
                status_code=429,
            )
        raise AuthError(
            f"Invalid email or password. {remaining} attempt(s) remaining.",
            status_code=401,
        )

    # Clear lockout on success
    await _clear_lockout(email, redis)

    # Build JWT payload
    token_data = {
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role,
        "email": user.email,
    }
    access_token = create_access_token(data=token_data)

    # Create refresh token
    raw_refresh = generate_refresh_token()
    hashed_refresh = hash_token(raw_refresh)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    refresh_obj = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=expires_at,
    )
    db.add(refresh_obj)

    # Update last_login_at
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    full_name = user.full_name

    user_ctx = UserContext(
        id=user.id,
        company_id=user.company_id,
        email=user.email,
        full_name=full_name,
        role=user.role.value if hasattr(user.role, 'value') else user.role,
    )

    response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_ctx,
    )
    return response, raw_refresh


async def refresh_token(
    token_str: str,
    db: AsyncSession,
) -> tuple[TokenRefreshResponse, str]:
    """
    Validate refresh token, rotate: revoke old, issue new pair.
    Returns (TokenRefreshResponse, new_raw_refresh_token).
    """
    from app.models.auth import User, RefreshToken

    hashed = hash_token(token_str)
    stmt = select(RefreshToken).where(
        RefreshToken.token_hash == hashed,
        RefreshToken.revoked_at.is_(None),
    )
    result = await db.execute(stmt)
    ref_token = result.scalar_one_or_none()

    if not ref_token:
        raise AuthError("Invalid or revoked refresh token.", status_code=401)

    if ref_token.expires_at < datetime.now(timezone.utc):
        ref_token.revoked_at = datetime.now(timezone.utc)
        await db.flush()
        raise AuthError("Refresh token expired.", status_code=401)

    # Revoke old token (rotation)
    ref_token.revoked_at = datetime.now(timezone.utc)

    # Fetch user
    user_stmt = select(User).where(User.id == ref_token.user_id, User.is_active.is_(True))
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    if not user:
        raise AuthError("User not found or deactivated.", status_code=401)

    # Issue new tokens
    token_data = {
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role,
        "email": user.email,
    }
    new_access = create_access_token(data=token_data)

    new_raw_refresh = generate_refresh_token()
    new_hashed = hash_token(new_raw_refresh)
    new_expires = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    new_ref = RefreshToken(
        user_id=user.id,
        token_hash=new_hashed,
        expires_at=new_expires,
    )
    db.add(new_ref)
    await db.flush()

    return TokenRefreshResponse(access_token=new_access), new_raw_refresh


async def logout(
    user_id: UUID,
    jti: str,
    token_exp: datetime,
    refresh_cookie: str | None,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> None:
    """
    Revoke the refresh token in DB and blacklist the access token's JTI
    in Redis with TTL = remaining token lifetime.
    """
    from app.models.auth import RefreshToken

    # Blacklist the JTI
    remaining = (token_exp - datetime.now(timezone.utc)).total_seconds()
    if remaining > 0:
        await redis.setex(f"blacklist:{jti}", int(remaining), "1")

    # Revoke refresh token
    if refresh_cookie:
        hashed = hash_token(refresh_cookie)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == hashed,
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        result = await db.execute(stmt)
        ref_token = result.scalar_one_or_none()
        if ref_token:
            ref_token.revoked_at = datetime.now(timezone.utc)
            await db.flush()


async def forgot_password(
    email: str,
    db: AsyncSession,
) -> None:
    """
    Generate a password reset token if user exists.
    Always returns None (caller sends 202 regardless to prevent user enumeration).
    """
    from app.models.auth import User, PasswordResetToken

    stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return  # Silently ignore — no enumeration

    raw_token = generate_reset_token()
    hashed = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + RESET_TOKEN_TTL

    reset_obj = PasswordResetToken(
        user_id=user.id,
        token_hash=hashed,
        expires_at=expires_at,
    )
    db.add(reset_obj)
    await db.flush()

    # TODO: Send email with reset link containing raw_token
    # For now, log it in debug mode
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Password reset token for {email}: {raw_token}")


async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession,
) -> None:
    """Validate a reset token and update the user's password."""
    from app.models.auth import User, PasswordResetToken

    hashed = hash_token(token)
    stmt = select(PasswordResetToken).where(
        PasswordResetToken.token_hash == hashed,
        PasswordResetToken.used_at.is_(None),
    )
    result = await db.execute(stmt)
    reset_obj = result.scalar_one_or_none()

    if not reset_obj:
        raise AuthError("Invalid or already used reset token.", status_code=400)

    if reset_obj.expires_at < datetime.now(timezone.utc):
        raise AuthError("Reset token has expired.", status_code=400)

    # Update password
    user_stmt = select(User).where(User.id == reset_obj.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    if not user:
        raise AuthError("User not found.", status_code=404)

    user.password_hash = hash_password(new_password)
    reset_obj.used_at = datetime.now(timezone.utc)
    await db.flush()


async def is_token_blacklisted(jti: str, redis: aioredis.Redis) -> bool:
    """Check if a JTI has been blacklisted (i.e. user logged out)."""
    return await redis.exists(f"blacklist:{jti}") > 0


async def get_user_context(user_id: UUID, db: AsyncSession) -> UserContext:
    """Fetch full user context for /me endpoint."""
    from app.models.auth import User
    from app.models.employee import Employee

    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise AuthError("User not found.", status_code=404)

    # Try to find linked employee
    employee_id = None
    emp_stmt = select(Employee.id).where(Employee.user_id == user.id, Employee.deleted_at.is_(None))
    emp_result = await db.execute(emp_stmt)
    emp = emp_result.scalar_one_or_none()
    if emp:
        employee_id = str(emp)

    return UserContext(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, 'value') else user.role,
        company_id=user.company_id,
    )
