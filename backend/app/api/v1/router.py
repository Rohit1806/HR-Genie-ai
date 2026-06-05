from fastapi import APIRouter
from app.api.v1 import (
    auth,
    employees,
    recruitment,
    attendance,
    leaves,
    payroll,
    performance,
    analytics,
    admin,
    ws,
    ai,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(recruitment.router, prefix="/recruitment", tags=["Recruitment"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["Leave"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["Payroll"])
api_router.include_router(performance.router, prefix="/performance", tags=["Performance"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Engine"])
api_router.include_router(ws.router, prefix="/ws", tags=["WebSockets"])
