from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import logging

from app.database import get_db
from app.redis_client import get_redis
from app.models.auth import User, UserRole, RefreshToken, PasswordResetToken
from app.models.organization import Company
from app.core.security import (
    verify_password, hash_password, create_access_token,
    generate_refresh_token, hash_token, generate_reset_token, decode_access_token
)
from app.core.dependencies import get_current_user
from app.config import settings
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserContext,
    TokenRefreshResponse, ForgotPasswordRequest, ResetPasswordRequest
)
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

COOKIE_NAME = "refresh_token"


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Authenticate user and issue tokens."""

    # Check rate limit (5 failed attempts → 15 min lockout)
    ip = request.client.host
    lockout_key = f"auth:lockout:{ip}:{body.email}"
    locked = await redis.get(lockout_key)
    if locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Try again in 15 minutes."
        )

    # Find user
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        # Track failed attempts
        attempts_key = f"auth:attempts:{ip}:{body.email}"
        attempts = await redis.incr(attempts_key)
        await redis.expire(attempts_key, 900)  # 15 min window

        if int(attempts) >= 5:
            await redis.set(lockout_key, "1", ex=900)  # Lock for 15 min
            await redis.delete(attempts_key)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended. Contact your administrator."
        )

    # Clear failed attempts on success
    await redis.delete(f"auth:attempts:{ip}:{body.email}")

    # Create access token
    access_token = create_access_token({
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role.value,
    })

    # Create refresh token
    raw_refresh = generate_refresh_token()
    hashed_refresh = hash_token(raw_refresh)
    refresh_expires = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    # Invalidate old refresh tokens for this user
    old_tokens = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None)
        )
    )
    for old_token in old_tokens.scalars().all():
        old_token.revoked_at = datetime.now(timezone.utc)

    # Store new refresh token
    db_refresh = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=refresh_expires,
    )
    db.add(db_refresh)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=raw_refresh,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )

    logger.info(f"User logged in: {user.email} ({user.role})")

    # Populate the full name from Employee if it exists!
    from app.models.employee import Employee
    emp_result = await db.execute(select(Employee).where(Employee.user_id == user.id))
    employee = emp_result.scalar_one_or_none()
    full_name = employee.full_name if employee else "System Administrator"

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserContext(
            id=user.id,
            company_id=user.company_id,
            email=user.email,
            full_name=full_name,
            role=user.role,
        ),
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Issue new access token using refresh token cookie."""

    raw_token = request.cookies.get(COOKIE_NAME)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    token_hash = hash_token(raw_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    db_token = result.scalar_one_or_none()

    if not db_token or not db_token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Fetch user
    result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or suspended"
        )

    # Rotate: revoke old, issue new
    db_token.revoked_at = datetime.now(timezone.utc)

    new_raw = generate_refresh_token()
    new_hash = hash_token(new_raw)
    new_expires = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    new_token = RefreshToken(
        user_id=user.id,
        token_hash=new_hash,
        expires_at=new_expires,
    )
    db.add(new_token)
    await db.commit()

    # New access token
    access_token = create_access_token({
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role.value,
    })

    # Rotate cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=new_raw,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )

    return TokenRefreshResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """Logout user — revoke refresh token and blacklist access token."""

    # Revoke refresh token
    raw_token = request.cookies.get(COOKIE_NAME)
    if raw_token:
        token_hash = hash_token(raw_token)
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        db_token = result.scalar_one_or_none()
        if db_token:
            db_token.revoked_at = datetime.now(timezone.utc)
            await db.commit()

    # Blacklist access token JTI in Redis
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = decode_access_token(token)
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                ttl = exp - int(datetime.now(timezone.utc).timestamp())
                if ttl > 0:
                    await redis.set(f"blacklist:token:{jti}", "1", ex=ttl)
        except Exception:
            pass

    # Clear cookie
    response.delete_cookie(key=COOKIE_NAME, path="/api/v1/auth")
    logger.info(f"User logged out: {current_user.email}")


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Initiate password reset (always returns 202 — never reveals if email exists)."""

    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user and user.is_active:
        token = generate_reset_token()
        token_hash = hash_token(token)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)

        db_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires,
        )
        db.add(db_token)
        await db.commit()

        # TODO: Send email with reset link
        # await send_reset_email(user.email, token)
        logger.info(f"Password reset requested for: {body.email}")

    return {"message": "If an account exists, a reset email has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Complete password reset using token."""

    token_hash = hash_token(body.token)
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
        )
    )
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    now = datetime.now(timezone.utc)
    if db_token.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )

    # Update password
    result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(body.new_password)
    db_token.used_at = now
    await db.commit()

    logger.info(f"Password reset completed for user: {user.id}")
    return {"message": "Password reset successful"}


@router.get("/me", response_model=UserContext)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user's profile."""
    from app.models.employee import Employee
    emp_result = await db.execute(select(Employee).where(Employee.user_id == current_user.id))
    employee = emp_result.scalar_one_or_none()
    full_name = employee.full_name if employee else "System Administrator"

    return UserContext(
        id=current_user.id,
        company_id=current_user.company_id,
        email=current_user.email,
        full_name=full_name,
        role=current_user.role,
    )
