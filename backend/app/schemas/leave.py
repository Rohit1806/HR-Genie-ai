from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional, List
from enum import Enum


class LeaveStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


# --- Leave Type ---
class LeaveTypeSchema(BaseModel):
    id: UUID
    name: str = ""
    code: str = ""
    annual_quota: int
    is_paid: bool
    carry_forward: bool

    class Config:
        from_attributes = True


# --- Leave Balance ---
class LeaveBalanceSchema(BaseModel):
    id: UUID
    leave_type: LeaveTypeSchema
    allocated: float
    used: float
    pending: float
    year: int

    class Config:
        from_attributes = True


# --- Leave Request ---
class LeaveRequestCreateSchema(BaseModel):
    leave_type_id: UUID
    from_date: date
    to_date: date
    reason: str


class LeaveRequestUpdateSchema(BaseModel):
    status: LeaveStatus


class LeaveApprovalSchema(BaseModel):
    id: UUID
    approver_name: Optional[str] = None
    action: str
    comment: Optional[str] = None
    actioned_at: datetime

    class Config:
        from_attributes = True


class LeaveRequestSchema(BaseModel):
    id: UUID
    employee_id: UUID
    leave_type: LeaveTypeSchema
    from_date: date
    to_date: date
    days_count: float
    reason: str
    status: LeaveStatus
    created_at: datetime
    approvals: List[LeaveApprovalSchema] = []

    class Config:
        from_attributes = True
