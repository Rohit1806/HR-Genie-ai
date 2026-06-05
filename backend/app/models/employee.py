from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Date, Enum as SAEnum, JSON, Index, Integer
from sqlalchemy import Numeric
from typing import Optional, List
from datetime import date
import uuid
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    NOTICE_PERIOD = "notice_period"
    TERMINATED = "terminated"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class Employee(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "employees"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[Gender]] = mapped_column(SAEnum(Gender, name="gender_enum"))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    personal_email: Mapped[Optional[str]] = mapped_column(String(255))
    address: Mapped[Optional[dict]] = mapped_column(JSON)
    emergency_contact: Mapped[Optional[dict]] = mapped_column(JSON)
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=False)
    employment_type: Mapped[EmploymentType] = mapped_column(
        SAEnum(EmploymentType, name="employment_type_enum"),
        default=EmploymentType.FULL_TIME,
    )
    employment_status: Mapped[EmploymentStatus] = mapped_column(
        SAEnum(EmploymentStatus, name="employment_status_enum"),
        default=EmploymentStatus.ACTIVE,
        index=True,
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
        index=True,
    )
    designation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("designations.id"),
        nullable=True,
    )
    reporting_manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("employees.id"),
        nullable=True,
        index=True,
    )
    work_location: Mapped[Optional[str]] = mapped_column(String(100))
    profile_photo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    department: Mapped[Optional["Department"]] = relationship(foreign_keys=[department_id])
    designation: Mapped[Optional["Designation"]] = relationship(foreign_keys=[designation_id])
    reporting_manager: Mapped[Optional["Employee"]] = relationship(
        foreign_keys=[reporting_manager_id],
        remote_side="Employee.id",
    )
    skills: Mapped[List["EmployeeSkill"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    documents: Mapped[List["EmployeeDocument"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    employment_history: Mapped[List["EmploymentHistory"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_employees_company_status", "company_id", "employment_status"),
        Index("idx_employees_department", "department_id"),
        Index("idx_employees_manager", "reporting_manager_id"),
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee {self.employee_code}: {self.full_name}>"


class Skill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100))


class EmployeeSkill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "employee_skills"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("skills.id"),
        nullable=False,
    )
    proficiency: Mapped[str] = mapped_column(String(20), default="beginner")
    years_experience: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship()


class EmploymentHistory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "employment_history"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_value: Mapped[Optional[dict]] = mapped_column(JSON)
    new_value: Mapped[Optional[dict]] = mapped_column(JSON)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500))
    recorded_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="employment_history")


class DocumentType(str, enum.Enum):
    OFFER_LETTER = "offer_letter"
    CONTRACT = "contract"
    ID_PROOF = "id_proof"
    CERTIFICATE = "certificate"
    PAYSLIP = "payslip"
    OTHER = "other"


class EmployeeDocument(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "employee_documents"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[DocumentType] = mapped_column(
        SAEnum(DocumentType, name="document_type_enum"),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str] = mapped_column(String(500))
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="documents")
