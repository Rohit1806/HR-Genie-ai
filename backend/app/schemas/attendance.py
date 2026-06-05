from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID
from typing import Optional
from enum import Enum


class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"
    late = "late"
    half_day = "half_day"
    on_leave = "on_leave"
    holiday = "holiday"


class RegularizationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


# --- Attendance Log ---
class AttendanceLogBaseSchema(BaseModel):
    date: date
    clock_in: datetime
    clock_out: Optional[datetime] = None
    status: AttendanceStatus


class AttendanceLogCreateSchema(AttendanceLogBaseSchema):
    pass


class AttendanceLogUpdateSchema(BaseModel):
    clock_out: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None
    total_hours: Optional[float] = None


class AttendanceLogSchema(AttendanceLogBaseSchema):
    id: UUID
    employee_id: UUID
    total_hours: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Regularization ---
class AttendanceRegularizationCreateSchema(BaseModel):
    date: date
    reason: str
    requested_clock_in: datetime
    requested_clock_out: datetime


class AttendanceRegularizationUpdateSchema(BaseModel):
    status: RegularizationStatus


class AttendanceRegularizationSchema(BaseModel):
    id: UUID
    employee_id: UUID
    date: date
    reason: str
    requested_clock_in: datetime
    requested_clock_out: datetime
    status: RegularizationStatus
    approved_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
