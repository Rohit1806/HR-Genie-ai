"""
Employee service for HRGenie AI.
Full employee lifecycle: create, list, update, terminate, org chart, skills, documents.
Role-scoped access: admin/HR = all, manager = reportees + self, employee = self only.
"""

import os
import uuid as _uuid
from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.auth import User
from app.models.organization import Department, Designation
from app.models.employee import (
    Employee,
    Skill,
    EmployeeSkill,
    EmploymentHistory,
    EmployeeDocument,
    EmploymentType,
    EmploymentStatus,
    DocumentType,
)
from app.schemas.employee import (
    EmployeeCreateSchema,
    EmployeeUpdateSchema,
    EmployeeSummarySchema,
    EmployeeDetailSchema,
    EmployeeListResponse,
    OrgChartNode,
    SkillSchema,
    DocumentSchema,
    HistorySchema,
)


class EmployeeServiceError(Exception):
    """Custom exception for employee service errors."""
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


async def _generate_employee_code(company_id: UUID, db: AsyncSession) -> str:
    """Generate unique employee code in format TN-{4digit}."""
    stmt = (
        select(func.count())
        .select_from(Employee)
        .where(Employee.company_id == company_id)
    )
    result = await db.execute(stmt)
    count = (result.scalar() or 0) + 1
    return f"TN-{count:04d}"


async def list_employees(
    company_id: UUID,
    role: str,
    user_id: UUID,
    department_id: UUID | None = None,
    status: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = None,
) -> EmployeeListResponse:
    """List employees with role-based scoping and filters."""
    query = (
        select(Employee)
        .where(Employee.company_id == company_id, Employee.deleted_at.is_(None))
    )

    # Role-based scoping
    if role == "employee":
        query = query.where(Employee.user_id == user_id)
    elif role == "manager":
        # Managers see reportees + self
        mgr_subquery = (
            select(Employee.id)
            .where(Employee.user_id == user_id)
            .scalar_subquery()
        )
        query = query.where(
            or_(
                Employee.reporting_manager_id == mgr_subquery,
                Employee.user_id == user_id,
            )
        )

    # Filters
    if department_id:
        query = query.where(Employee.department_id == department_id)
    if status:
        query = query.where(Employee.employment_status == status)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(Employee.first_name).like(search_term),
                func.lower(Employee.last_name).like(search_term),
                func.lower(Employee.employee_code).like(search_term),
            )
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Employee.created_at.desc())

    # Eager load relationships
    query = query.options(
        selectinload(Employee.department),
        selectinload(Employee.designation),
    )

    result = await db.execute(query)
    employees = result.scalars().all()

    items = []
    for emp in employees:
        items.append(
            EmployeeSummarySchema(
                id=emp.id,
                employee_code=emp.employee_code,
                full_name=f"{emp.first_name} {emp.last_name}",
                department_name=emp.department.name if emp.department else None,
                designation_title=emp.designation.title if emp.designation else None,
                employment_status=emp.employment_status.value if hasattr(emp.employment_status, 'value') else emp.employment_status,
                profile_photo_url=emp.profile_photo_url,
                date_of_joining=emp.date_of_joining,
            )
        )

    total_pages = (total + page_size - 1) // page_size

    return EmployeeListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


async def get_employee_detail(
    employee_id: UUID,
    company_id: UUID,
    requesting_user_id: UUID,
    requesting_role: str,
    db: AsyncSession,
) -> EmployeeDetailSchema | None:
    """Get full employee profile with skills, documents, and manager info."""
    stmt = (
        select(Employee)
        .where(
            Employee.id == employee_id,
            Employee.company_id == company_id,
            Employee.deleted_at.is_(None),
        )
        .options(
            selectinload(Employee.department),
            selectinload(Employee.designation),
            selectinload(Employee.manager),
        )
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if not employee:
        return None

    # Access check
    if requesting_role == "employee" and employee.user_id != requesting_user_id:
        raise EmployeeServiceError("Access denied: cannot view other employee profiles.", status_code=403)
    if requesting_role == "manager":
        # Check if requesting user is the manager
        mgr_stmt = select(Employee.id).where(
            Employee.user_id == requesting_user_id,
            Employee.company_id == company_id,
        )
        mgr_result = await db.execute(mgr_stmt)
        mgr_id = mgr_result.scalar_one_or_none()
        if (
            employee.user_id != requesting_user_id
            and employee.reporting_manager_id != mgr_id
        ):
            raise EmployeeServiceError("Access denied: not your reportee.", status_code=403)

    # Fetch Skills junction with Skill details
    skills_stmt = (
        select(EmployeeSkill)
        .where(EmployeeSkill.employee_id == employee_id)
        .options(selectinload(EmployeeSkill.skill))
    )
    skills_result = await db.execute(skills_stmt)
    emp_skills = skills_result.scalars().all()

    # Fetch Documents
    docs_stmt = select(EmployeeDocument).where(
        EmployeeDocument.employee_id == employee_id,
        EmployeeDocument.deleted_at.is_(None),
    )
    docs_result = await db.execute(docs_stmt)
    documents = docs_result.scalars().all()

    # Fetch History
    history_stmt = select(EmploymentHistory).where(
        EmploymentHistory.employee_id == employee_id
    ).order_by(EmploymentHistory.effective_date.desc())
    history_result = await db.execute(history_stmt)
    history_records = history_result.scalars().all()

    skills_schema = [
        SkillSchema(
            id=s.id,
            name=s.skill.name,
            category=s.skill.category,
            proficiency=s.proficiency.value if hasattr(s.proficiency, 'value') else s.proficiency,
            years_experience=s.years_experience,
        )
        for s in emp_skills if s.skill
    ]

    docs_schema = [
        DocumentSchema(
            id=d.id,
            document_type=d.document_type.value if hasattr(d.document_type, 'value') else d.document_type,
            file_name=d.file_name,
            file_url=d.file_url,
            file_size_bytes=d.file_size_bytes,
            created_at=d.created_at,
        )
        for d in documents
    ]

    history_schema = [
        HistorySchema(
            id=h.id,
            event_type=h.event_type,
            previous_value=h.previous_value,
            new_value=h.new_value,
            effective_date=h.effective_date,
            reason=h.reason,
        )
        for h in history_records
    ]

    manager_name = None
    if employee.manager:
        manager_name = f"{employee.manager.first_name} {employee.manager.last_name}"

    return EmployeeDetailSchema(
        id=employee.id,
        employee_code=employee.employee_code,
        full_name=f"{employee.first_name} {employee.last_name}",
        department_name=employee.department.name if employee.department else None,
        designation_title=employee.designation.title if employee.designation else None,
        employment_status=employee.employment_status.value if hasattr(employee.employment_status, 'value') else employee.employment_status,
        profile_photo_url=employee.profile_photo_url,
        date_of_joining=employee.date_of_joining,
        personal_email=employee.personal_email,
        phone=employee.phone,
        date_of_birth=employee.date_of_birth,
        gender=employee.gender,
        address=employee.address,
        emergency_contact=employee.emergency_contact,
        reporting_manager_name=manager_name,
        skills=skills_schema,
        documents=docs_schema,
        history=history_schema,
    )


async def create_employee(
    data: EmployeeCreateSchema,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Create a new employee with auto-generated employee code."""
    from app.core.security import hash_password

    # Generate unique employee code
    employee_code = await _generate_employee_code(company_id, db)

    # Create user account for this employee
    user = User(
        email=data.personal_email,
        password_hash=hash_password("Welcome@123"),  # Default password
        full_name=f"{data.first_name} {data.last_name}",
        role="employee",
        company_id=company_id,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    # Create employee record
    employee = Employee(
        user_id=user.id,
        company_id=company_id,
        employee_code=employee_code,
        first_name=data.first_name,
        last_name=data.last_name,
        personal_email=data.personal_email,
        phone=data.phone,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        address=data.address,
        emergency_contact=data.emergency_contact,
        department_id=data.department_id,
        designation_id=data.designation_id,
        reporting_manager_id=data.reporting_manager_id,
        date_of_joining=data.date_of_joining or date.today(),
        employment_type=EmploymentType(data.employment_type) if isinstance(data.employment_type, str) else data.employment_type,
        employment_status=EmploymentStatus.active,
        work_location=data.work_location,
    )
    db.add(employee)
    await db.flush()
    await db.refresh(employee)

    # Log initial history
    history = EmploymentHistory(
        employee_id=employee.id,
        event_type="onboarding",
        previous_value=None,
        new_value={"status": "onboarded", "code": employee.employee_code},
        effective_date=employee.date_of_joining,
    )
    db.add(history)
    await db.flush()

    return {
        "id": str(employee.id),
        "employee_code": employee.employee_code,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.personal_email,
        "status": employee.employment_status.value if hasattr(employee.employment_status, 'value') else employee.employment_status,
        "default_password": "Welcome@123",
    }


async def update_employee(
    id: UUID,
    data: EmployeeUpdateSchema,
    company_id: UUID,
    db: AsyncSession,
) -> dict | None:
    """Update employee fields and log change history."""
    stmt = select(Employee).where(
        Employee.id == id,
        Employee.company_id == company_id,
        Employee.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if not employee:
        return None

    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        old_value = getattr(employee, field, None)
        if old_value != value:
            # Handle enum conversion if needed
            if field == "employment_type" and isinstance(value, str):
                value = EmploymentType(value)
            elif field == "employment_status" and isinstance(value, str):
                value = EmploymentStatus(value)
                
            # Log history
            history = EmploymentHistory(
                employee_id=employee.id,
                event_type="update",
                previous_value={field: str(old_value.value if hasattr(old_value, 'value') else old_value) if old_value is not None else None},
                new_value={field: str(value.value if hasattr(value, 'value') else value)},
                effective_date=date.today(),
            )
            db.add(history)
            setattr(employee, field, value)

    employee.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(employee)

    return {
        "id": str(employee.id),
        "employee_code": employee.employee_code,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.personal_email,
        "status": employee.employment_status.value if hasattr(employee.employment_status, 'value') else employee.employment_status,
    }


async def terminate_employee(
    id: UUID,
    reason: str,
    termination_date: date,
    admin_user_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> dict | None:
    """Terminate an employee — set status, soft delete."""
    stmt = select(Employee).where(
        Employee.id == id,
        Employee.company_id == company_id,
        Employee.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if not employee:
        return None

    # Log history
    history = EmploymentHistory(
        employee_id=employee.id,
        event_type="termination",
        previous_value={"status": employee.employment_status.value if hasattr(employee.employment_status, 'value') else employee.employment_status},
        new_value={"status": "terminated", "reason": reason, "date": termination_date.isoformat(), "terminated_by": str(admin_user_id)},
        effective_date=termination_date,
    )
    db.add(history)

    employee.employment_status = EmploymentStatus.terminated
    employee.deleted_at = datetime.now(timezone.utc)
    employee.updated_at = datetime.now(timezone.utc)

    # Deactivate user account
    if employee.user_id:
        user_stmt = select(User).where(User.id == employee.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if user:
            user.is_active = False
            user.deleted_at = datetime.now(timezone.utc)

    await db.flush()

    return {
        "id": str(employee.id),
        "employee_code": employee.employee_code,
        "status": "terminated",
        "termination_date": termination_date.isoformat(),
    }


async def get_org_chart(
    company_id: UUID,
    db: AsyncSession,
) -> list[OrgChartNode]:
    """Build nested org tree from reporting_manager_id relationships."""
    stmt = (
        select(Employee)
        .where(
            Employee.company_id == company_id,
            Employee.employment_status == EmploymentStatus.active,
            Employee.deleted_at.is_(None),
        )
        .options(
            selectinload(Employee.designation),
            selectinload(Employee.department),
        )
    )
    result = await db.execute(stmt)
    employees = result.scalars().all()

    # Build lookup
    nodes: dict[str, OrgChartNode] = {}
    for emp in employees:
        nodes[str(emp.id)] = OrgChartNode(
            id=emp.id,
            name=f"{emp.first_name} {emp.last_name}",
            designation=emp.designation.title if emp.designation else "Employee",
            department=emp.department.name if emp.department else "General",
            photo_url=emp.profile_photo_url,
            children=[],
        )

    # Build tree
    roots: list[OrgChartNode] = []
    for emp in employees:
        node = nodes[str(emp.id)]
        if emp.reporting_manager_id and str(emp.reporting_manager_id) in nodes:
            nodes[str(emp.reporting_manager_id)].children.append(node)
        else:
            roots.append(node)

    return roots


async def add_skill(
    employee_id: UUID,
    skill_name: str,
    proficiency_level: str,
    years_experience: float | None,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Add a skill to an employee. Creates Skill if not exists."""
    # Verify employee
    emp_stmt = select(Employee).where(
        Employee.id == employee_id,
        Employee.company_id == company_id,
        Employee.deleted_at.is_(None),
    )
    result = await db.execute(emp_stmt)
    employee = result.scalar_one_or_none()
    if not employee:
        raise EmployeeServiceError("Employee not found", status_code=404)

    # Find or create skill in global Skill table
    skill_stmt = select(Skill).where(Skill.name == skill_name)
    skill_result = await db.execute(skill_stmt)
    skill = skill_result.scalar_one_or_none()
    
    if not skill:
        skill = Skill(
            name=skill_name,
            category="General",
        )
        db.add(skill)
        await db.flush()

    # Check if EmployeeSkill relationship already exists
    es_stmt = select(EmployeeSkill).where(
        EmployeeSkill.employee_id == employee_id,
        EmployeeSkill.skill_id == skill.id,
    )
    es_result = await db.execute(es_stmt)
    es = es_result.scalar_one_or_none()
    
    if es:
        # Update existing
        es.proficiency = proficiency_level
        if years_experience is not None:
            es.years_experience = years_experience
    else:
        # Create new mapping
        es = EmployeeSkill(
            employee_id=employee_id,
            skill_id=skill.id,
            proficiency=proficiency_level,
            years_experience=years_experience,
        )
        db.add(es)
        
    await db.flush()
    await db.refresh(es)

    return {
        "id": str(es.id),
        "skill_name": skill.name,
        "proficiency_level": es.proficiency.value if hasattr(es.proficiency, 'value') else es.proficiency,
        "years_experience": es.years_experience,
    }


async def upload_document(
    employee_id: UUID,
    file_name: str,
    file_content: bytes,
    document_type: str,
    company_id: UUID,
    db: AsyncSession,
) -> dict:
    """Upload and store a document for an employee."""
    # Verify employee
    stmt = select(Employee).where(
        Employee.id == employee_id,
        Employee.company_id == company_id,
        Employee.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    if not employee:
        raise EmployeeServiceError("Employee not found", status_code=404)

    # Save file on filesystem
    upload_dir = os.path.join(settings.UPLOAD_DIR, "documents", str(employee_id))
    os.makedirs(upload_dir, exist_ok=True)

    unique_name = f"{_uuid.uuid4().hex}_{file_name}"
    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(file_content)

    doc = EmployeeDocument(
        employee_id=employee_id,
        document_type=DocumentType(document_type),
        file_name=file_name,
        file_url=file_path,
        file_size_bytes=len(file_content),
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    return {
        "id": str(doc.id),
        "document_type": doc.document_type.value if hasattr(doc.document_type, 'value') else doc.document_type,
        "file_name": doc.file_name,
        "file_url": doc.file_url,
        "uploaded_at": doc.created_at.isoformat() if doc.created_at else None,
    }


async def get_employee_documents(
    employee_id: UUID,
    company_id: UUID,
    db: AsyncSession,
) -> list[dict]:
    """List all documents for an employee."""
    # Verify employee
    stmt = select(Employee).where(
        Employee.id == employee_id,
        Employee.company_id == company_id,
        Employee.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    if not employee:
        raise EmployeeServiceError("Employee not found", status_code=404)

    docs_stmt = select(EmployeeDocument).where(
        EmployeeDocument.employee_id == employee_id,
        EmployeeDocument.deleted_at.is_(None),
    )
    docs_result = await db.execute(docs_stmt)
    docs = docs_result.scalars().all()

    return [
        {
            "id": str(d.id),
            "document_type": d.document_type.value if hasattr(d.document_type, 'value') else d.document_type,
            "file_name": d.file_name,
            "file_url": d.file_url,
            "file_size": d.file_size_bytes,
            "uploaded_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]
