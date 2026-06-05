"""
Employees API router for HRGenie AI.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac import require_hr
from app.models.auth import User
from app.schemas.employee import (
    EmployeeCreateSchema,
    EmployeeUpdateSchema,
    EmployeeListResponse,
    EmployeeDetailSchema,
    OrgChartNode,
)
from app.services import employee_service
from app.core.exceptions import ValidationError, NotFoundError

router = APIRouter()


@router.get("/", response_model=EmployeeListResponse)
async def list_employees(
    department_id: Optional[UUID] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List employees in the company. Includes role-based scoping:
    - Admin/HR: View all
    - Manager: View self + reportees
    - Employee: View self only
    """
    return await employee_service.list_employees(
        company_id=current_user.company_id,
        role=current_user.role,
        user_id=current_user.id,
        department_id=department_id,
        status=status,
        search=search,
        page=page,
        page_size=page_size,
        db=db,
    )


@router.get("/org-chart", response_model=list[OrgChartNode])
async def get_org_chart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get nested organizational hierarchy chart.
    """
    return await employee_service.get_org_chart(
        company_id=current_user.company_id,
        db=db,
    )


@router.get("/{id}", response_model=EmployeeDetailSchema)
async def get_employee_detail(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get full details for a single employee profile.
    """
    profile = await employee_service.get_employee_detail(
        employee_id=id,
        company_id=current_user.company_id,
        requesting_user_id=current_user.id,
        requesting_role=current_user.role,
        db=db,
    )
    if not profile:
        raise NotFoundError("Employee profile not found.")
    return profile


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_hr)])
async def create_employee(
    data: EmployeeCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new employee profile and its associated user account. (HR/Admin only)
    """
    return await employee_service.create_employee(
        data=data,
        company_id=current_user.company_id,
        db=db,
    )


@router.patch("/{id}", response_model=dict)
async def update_employee(
    id: UUID,
    data: EmployeeUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update employee profile information. (HR/Admin or self edit)
    """
    # Permission: HR/Admin can update anyone; others can only update themselves
    if current_user.role not in ["admin", "hr_recruiter"]:
        # Find if employee matches current_user
        profile = await employee_service.get_employee_detail(
            employee_id=id,
            company_id=current_user.company_id,
            requesting_user_id=current_user.id,
            requesting_role=current_user.role,
            db=db,
        )
        if not profile or profile.id != id:
            raise ValidationError("Access denied: cannot update other employee profiles.")

    res = await employee_service.update_employee(
        id=id,
        data=data,
        company_id=current_user.company_id,
        db=db,
    )
    if not res:
        raise NotFoundError("Employee not found.")
    return res


@router.delete("/{id}", response_model=dict, dependencies=[Depends(require_hr)])
async def terminate_employee(
    id: UUID,
    reason: str = Query(...),
    termination_date: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Terminate an employee profile and deactivate user login. (HR/Admin only)
    """
    try:
        t_date = datetime.strptime(termination_date, "%Y-%m-%d").date()
    except Exception:
        raise ValidationError("Invalid date format. Expected YYYY-MM-DD")

    res = await employee_service.terminate_employee(
        id=id,
        reason=reason,
        termination_date=t_date,
        admin_user_id=current_user.id,
        company_id=current_user.company_id,
        db=db,
    )
    if not res:
        raise NotFoundError("Employee profile not found.")
    return res


@router.post("/{id}/skills", response_model=dict)
async def add_skill(
    id: UUID,
    skill_name: str = Form(...),
    proficiency_level: str = Form(...),
    years_experience: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add or update a skill mapping for an employee.
    """
    # Permission: HR/Admin can edit anyone; others can only edit themselves
    if current_user.role not in ["admin", "hr_recruiter"]:
        profile = await employee_service.get_employee_detail(
            employee_id=id,
            company_id=current_user.company_id,
            requesting_user_id=current_user.id,
            requesting_role=current_user.role,
            db=db,
        )
        if not profile:
            raise NotFoundError("Employee not found.")

    return await employee_service.add_skill(
        employee_id=id,
        skill_name=skill_name,
        proficiency_level=proficiency_level,
        years_experience=years_experience,
        company_id=current_user.company_id,
        db=db,
    )


@router.post("/{id}/documents", response_model=dict)
async def upload_document(
    id: UUID,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and save a document for an employee. (HR/Admin or self)
    """
    # Permission check
    if current_user.role not in ["admin", "hr_recruiter"]:
        profile = await employee_service.get_employee_detail(
            employee_id=id,
            company_id=current_user.company_id,
            requesting_user_id=current_user.id,
            requesting_role=current_user.role,
            db=db,
        )
        if not profile:
            raise NotFoundError("Employee not found.")

    contents = await file.read()
    return await employee_service.upload_document(
        employee_id=id,
        file_name=file.filename or "upload.pdf",
        file_content=contents,
        document_type=document_type,
        company_id=current_user.company_id,
        db=db,
    )


@router.get("/{id}/documents", response_model=list[dict])
async def get_employee_documents(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all uploaded documents for an employee.
    """
    # Permission check
    if current_user.role not in ["admin", "hr_recruiter"]:
        profile = await employee_service.get_employee_detail(
            employee_id=id,
            company_id=current_user.company_id,
            requesting_user_id=current_user.id,
            requesting_role=current_user.role,
            db=db,
        )
        if not profile:
            raise NotFoundError("Employee not found.")

    return await employee_service.get_employee_documents(
        employee_id=id,
        company_id=current_user.company_id,
        db=db,
    )
