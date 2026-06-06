from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy import Index
from typing import Optional, List
from datetime import datetime
import uuid
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SENIOR_MANAGER = "senior_manager"
    HR_RECRUITER = "hr_recruiter"
    EMPLOYEE = "employee"


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens: Mapped[List["PasswordResetToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_users_company_email", "company_id", "email"),
        Index("idx_users_company_role", "company_id", "role"),
    )

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class RefreshToken(Base, UUIDMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    @property
    def is_valid(self) -> bool:
        from datetime import timezone
        return (
            self.revoked_at is None
            and self.expires_at > datetime.now(timezone.utc)
        )


class PasswordResetToken(Base, UUIDMixin):
    __tablename__ = "password_reset_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="password_reset_tokens")
