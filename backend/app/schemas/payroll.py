from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from enum import Enum


class PayrollStatus(str, Enum):
    draft = "draft"
    computing = "computing"
    computed = "computed"
    approved = "approved"
    paid = "paid"


# --- Salary Structure Component ---
class SalaryComponent(BaseModel):
    name: str
    type: str  # earning or deduction
    value: float
    is_percentage: bool
    taxable: bool


# --- Salary Structure ---
class SalaryStructureCreateSchema(BaseModel):
    name: str
    components: List[SalaryComponent] = []


class SalaryStructureSchema(BaseModel):
    id: UUID
    name: str
    components: List[SalaryComponent] = []

    class Config:
        from_attributes = True


# --- Employee Salary ---
class EmployeeSalaryCreateSchema(BaseModel):
    employee_id: UUID
    salary_structure_id: Optional[UUID] = None
    gross_salary: float
    effective_from: date


class EmployeeSalarySchema(BaseModel):
    id: UUID
    employee_id: UUID
    salary_structure_id: Optional[UUID] = None
    gross_salary: float
    effective_from: date

    class Config:
        from_attributes = True


# --- Payroll Run ---
class PayrollRunCreateSchema(BaseModel):
    month: int
    year: int


class PayrollRunUpdateSchema(BaseModel):
    status: PayrollStatus


# --- Payroll Entry ---
class PayrollEntrySchema(BaseModel):
    id: UUID
    payroll_run_id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None
    gross_salary: float
    basic: float
    hra: float
    allowances: Optional[Dict[str, Any]] = None
    pf_deduction: float
    esi_deduction: float
    tds_deduction: float
    lop_days: int
    lop_deduction: float
    net_salary: float

    class Config:
        from_attributes = True


class PayrollRunSchema(BaseModel):
    id: UUID
    month: int
    year: int
    status: PayrollStatus
    total_gross: Optional[float] = None
    total_net: Optional[float] = None
    initiated_by: Optional[UUID] = None
    entries: List[PayrollEntrySchema] = []

    class Config:
        from_attributes = True
