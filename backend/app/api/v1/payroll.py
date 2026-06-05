"""
Payroll API router for HRGenie AI.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.auth import User, UserRole
from app.models.employee import Employee
from app.services import payroll_service
from app.schemas.payroll import PayrollRunCreateSchema

router = APIRouter()


async def _get_employee(user: User, db: AsyncSession) -> Employee:
    """Helper dependency to retrieve employee from the active user session."""
    stmt = select(Employee).where(
        Employee.user_id == user.id,
        Employee.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found for this user."
        )
    return employee


@router.post("/runs", response_model=dict)
async def initiate_payroll_run(
    data: PayrollRunCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate and compute a payroll run for a specific month and year (HR/Admin only).
    """
    if current_user.role not in (UserRole.admin, UserRole.hr_recruiter):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only Admin or HR roles can run payroll."
        )

    try:
        # 1. Initiate run
        run_res = await payroll_service.initiate_payroll(
            company_id=current_user.company_id,
            month=data.month,
            year=data.year,
            user_id=current_user.id,
            db=db,
        )
        # 2. Compute entries immediately
        run_id = UUID(run_res["id"])
        compute_res = await payroll_service.compute_payroll(
            run_id=run_id,
            company_id=current_user.company_id,
            db=db,
        )
        return compute_res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/runs", response_model=dict)
async def list_payroll_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all payroll runs in the company (HR/Admin only).
    """
    if current_user.role not in (UserRole.admin, UserRole.hr_recruiter):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Authorized roles only."
        )

    runs = await payroll_service.get_payroll_runs(
        company_id=current_user.company_id,
        db=db,
    )
    total = len(runs)
    offset = (page - 1) * page_size
    items = runs[offset:offset + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }


@router.get("/runs/{id}", response_model=dict)
async def get_payroll_run_status(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed status of a payroll run.
    """
    from app.models.payroll import PayrollRun
    stmt = select(PayrollRun).where(
        PayrollRun.id == id,
        PayrollRun.company_id == current_user.company_id,
    )
    res = await db.execute(stmt)
    run = res.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll run not found.")

    return {
        "id": str(run.id),
        "month": run.month,
        "year": run.year,
        "status": run.status.value,
        "total_gross": float(run.total_gross) if run.total_gross else 0.0,
        "total_net": float(run.total_net) if run.total_net else 0.0,
        "initiated_at": run.created_at.isoformat() if run.created_at else None,
    }


@router.get("/runs/{id}/entries", response_model=dict)
async def get_payroll_run_entries(
    id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all salary computation entries for a specific payroll run (HR/Admin only).
    """
    if current_user.role not in (UserRole.admin, UserRole.hr_recruiter):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    entries = await payroll_service.get_payroll_entries(
        run_id=id,
        company_id=current_user.company_id,
        db=db,
    )
    total = len(entries)
    offset = (page - 1) * page_size
    items = entries[offset:offset + page_size]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
    }


@router.patch("/runs/{id}/approve", response_model=dict)
async def approve_payroll_run(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve a computed payroll run (Admin/Senior Manager only).
    """
    if current_user.role not in (UserRole.admin, UserRole.senior_manager):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only admin or senior managers can approve payroll."
        )

    try:
        return await payroll_service.approve_payroll(
            run_id=id,
            company_id=current_user.company_id,
            approver_id=current_user.id,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my-payslip", response_model=dict)
async def get_my_payslip(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the monthly payslip for the current logged-in employee.
    """
    employee = await _get_employee(current_user, db)
    payslip = await payroll_service.get_payslip(
        employee_id=employee.id,
        month=month,
        year=year,
        company_id=current_user.company_id,
        db=db,
    )
    if not payslip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payslip not found for the requested period. Check if payroll was approved."
        )

    # Map to frontend structure containing nested records
    return {
        "month": payslip.month,
        "year": payslip.year,
        "employee_name": payslip.employee_name,
        "employee_code": payslip.employee_code,
        "department": employee.department.name if employee.department else "General",
        "designation": employee.designation.title if employee.designation else "Employee",
        "earnings": {
            "Basic Salary": payslip.basic,
            "HRA": payslip.hra,
            "Allowances": payslip.allowances,
        },
        "deductions": {
            "Provident Fund (PF)": payslip.pf_deduction,
            "ESI": payslip.esi_deduction,
            "TDS": payslip.tds_deduction,
            "Loss of Pay (LOP)": payslip.lop_deduction,
        },
        "gross_salary": payslip.gross_salary,
        "total_deductions": payslip.total_deductions,
        "net_salary": payslip.net_salary,
    }
