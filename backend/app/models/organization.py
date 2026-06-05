from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Index
from typing import Optional, List
import uuid

from app.models.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


class Company(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata")
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    departments: Mapped[List["Department"]] = relationship(back_populates="company")
    designations: Mapped[List["Designation"]] = relationship(back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"


class Department(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "departments"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="departments")
    parent: Mapped[Optional["Department"]] = relationship(
        remote_side="Department.id", back_populates="children"
    )
    children: Mapped[List["Department"]] = relationship(back_populates="parent")

    __table_args__ = (
        Index("idx_departments_company", "company_id"),
    )

    def __repr__(self):
        return f"<Department {self.name}>"


class Designation(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "designations"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="designations")

    __table_args__ = (
        Index("idx_designations_company", "company_id"),
    )

    def __repr__(self):
        return f"<Designation {self.title}>"
