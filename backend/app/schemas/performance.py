from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from enum import Enum


class CycleType(str, Enum):
    quarterly = "quarterly"
    half_yearly = "half_yearly"
    annual = "annual"


class CycleStatus(str, Enum):
    upcoming = "upcoming"
    active = "active"
    review = "review"
    completed = "completed"


class GoalStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    deferred = "deferred"


class ReviewType(str, Enum):
    self_review = "self_review"
    manager_review = "manager_review"
    peer_review = "peer_review"


# --- Goal ---
class KeyResultSchema(BaseModel):
    title: str
    target: float
    current: float = 0.0


class GoalCreateSchema(BaseModel):
    cycle_id: UUID
    title: str
    description: Optional[str] = None
    key_results: List[KeyResultSchema] = []
    weightage: float = 0.0
    status: GoalStatus = GoalStatus.not_started
    due_date: Optional[date] = None


class GoalUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    key_results: Optional[List[KeyResultSchema]] = None
    weightage: Optional[float] = None
    status: Optional[GoalStatus] = None
    due_date: Optional[date] = None


class GoalSchema(BaseModel):
    id: UUID
    employee_id: UUID
    cycle_id: UUID
    title: str
    description: Optional[str] = None
    key_results: List[KeyResultSchema] = []
    weightage: float
    status: GoalStatus
    due_date: Optional[date] = None

    class Config:
        from_attributes = True


# --- Review ---
class PerformanceReviewCreateSchema(BaseModel):
    cycle_id: UUID
    employee_id: UUID
    review_type: ReviewType
    ratings: Dict[str, float] = {}
    feedback: Optional[str] = None
    overall_score: Optional[float] = None


class PerformanceReviewSchema(BaseModel):
    id: UUID
    cycle_id: UUID
    employee_id: UUID
    reviewer_id: Optional[UUID] = None
    review_type: ReviewType
    ratings: Dict[str, float] = {}
    feedback: Optional[str] = None
    overall_score: Optional[float] = None
    ai_summary: Optional[str] = None

    class Config:
        from_attributes = True


# --- Cycle ---
class PerformanceCycleSchema(BaseModel):
    id: UUID
    name: str
    cycle_type: CycleType
    start_date: date
    end_date: date
    review_start: date
    review_end: date
    status: CycleStatus

    class Config:
        from_attributes = True


# --- Score ---
class PerformanceScoreSchema(BaseModel):
    id: UUID
    cycle_id: UUID
    employee_id: UUID
    goal_score: Optional[float] = None
    self_score: Optional[float] = None
    manager_score: Optional[float] = None
    final_score: Optional[float] = None
    ai_promotion_score: Optional[float] = None
    ai_attrition_risk: Optional[float] = None

    class Config:
        from_attributes = True
