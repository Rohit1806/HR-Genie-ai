import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Adjust path to import app modules correctly
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.core.security import hash_password
from app.models.auth import User, UserRole
from app.models.organization import Company, Department, Designation
from app.models.employee import Employee, Skill, EmployeeSkill, EmployeeDocument, EmploymentType, EmploymentStatus, DocumentType
from app.models.attendance import AttendanceLog, AttendanceRegularization, AttendanceStatus, RegularizationStatus
from app.models.leave import LeaveType, LeaveBalance, LeaveRequest, LeaveApproval, Holiday, LeaveStatus
from app.models.payroll import SalaryStructure, EmployeeSalary, PayrollRun, PayrollEntry, PayrollStatus
from app.models.performance import PerformanceCycle, Goal, PerformanceReview, PerformanceScore, CycleType, CycleStatus, GoalStatus, ReviewType
from app.models.recruitment import JobPosting, Candidate, Application, AIEvaluation, JobStatus, ApplicationStage
from app.models.notification import Notification


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        try:
            # 1. Fetch or create company
            company_stmt = select(Company).where(Company.slug == "demo-company")
            res = await db.execute(company_stmt)
            company = res.scalar_one_or_none()
            if not company:
                company = Company(name="Demo Company", slug="demo-company", timezone="Asia/Kolkata", currency="INR")
                db.add(company)
                await db.flush()
            print(f"  [OK] Company: {company.name}")

            # 2. Departments
            depts = {}
            for dept_name in ["Engineering", "Human Resources", "Sales", "Finance"]:
                stmt = select(Department).where(Department.company_id == company.id, Department.name == dept_name)
                res = await db.execute(stmt)
                dept = res.scalar_one_or_none()
                if not dept:
                    dept = Department(company_id=company.id, name=dept_name)
                    db.add(dept)
                    await db.flush()
                depts[dept_name] = dept
            print(f"  [OK] Departments: {list(depts.keys())}")

            # 3. Designations
            desgs = {}
            designation_list = [
                "Chief Technical Officer",
                "Software Engineer",
                "HR Director",
                "Talent Recruiter",
                "Sales Executive",
                "Finance Head",
            ]
            for title in designation_list:
                stmt = select(Designation).where(Designation.company_id == company.id, Designation.title == title)
                res = await db.execute(stmt)
                desg = res.scalar_one_or_none()
                if not desg:
                    desg = Designation(company_id=company.id, title=title)
                    db.add(desg)
                    await db.flush()
                desgs[title] = desg
            print(f"  [OK] Designations: {list(desgs.keys())}")

            # 4. Users and Employees
            # Note: User model does NOT have full_name; only email, password_hash, role, is_active, is_2fa_enabled
            employees_data = [
                {
                    "email": "admin@demo.hrgenie.ai",
                    "role": UserRole.ADMIN,
                    "code": "EMP001",
                    "first": "System",
                    "last": "Administrator",
                    "title": "Chief Technical Officer",
                    "dept": "Engineering",
                    "phone": "+91 99999 88888",
                },
                {
                    "email": "hr@demo.hrgenie.ai",
                    "role": UserRole.HR_RECRUITER,
                    "code": "EMP002",
                    "first": "Sarah",
                    "last": "Connor",
                    "title": "HR Director",
                    "dept": "Human Resources",
                    "phone": "+91 99999 77777",
                },
                {
                    "email": "manager@demo.hrgenie.ai",
                    "role": UserRole.SENIOR_MANAGER,
                    "code": "EMP003",
                    "first": "John",
                    "last": "Manager",
                    "title": "Finance Head",
                    "dept": "Finance",
                    "phone": "+91 99999 66666",
                },
                {
                    "email": "employee@demo.hrgenie.ai",
                    "role": UserRole.EMPLOYEE,
                    "code": "EMP004",
                    "first": "Rohit",
                    "last": "Sharma",
                    "title": "Software Engineer",
                    "dept": "Engineering",
                    "phone": "+91 99999 55555",
                },
            ]

            seeded_employees = {}
            for item in employees_data:
                # Check User
                user_stmt = select(User).where(User.company_id == company.id, User.email == item["email"])
                res = await db.execute(user_stmt)
                user = res.scalar_one_or_none()
                if not user:
                    user = User(
                        company_id=company.id,
                        email=item["email"],
                        password_hash=hash_password("Demo@1234"),
                        role=item["role"],
                        full_name=f"{item['first']} {item['last']}",
                    )
                    db.add(user)
                    await db.flush()

                # Check Employee
                emp_stmt = select(Employee).where(Employee.user_id == user.id)
                res = await db.execute(emp_stmt)
                emp = res.scalar_one_or_none()
                if not emp:
                    emp = Employee(
                        company_id=company.id,
                        user_id=user.id,
                        employee_code=item["code"],
                        first_name=item["first"],
                        last_name=item["last"],
                        date_of_birth=date(1992, 4, 15),
                        gender="male",
                        phone=item["phone"],
                        personal_email=item["email"],
                        date_of_joining=date(2026, 1, 1),
                        employment_type=EmploymentType.FULL_TIME,
                        employment_status=EmploymentStatus.ACTIVE,
                        department_id=depts[item["dept"]].id,
                        designation_id=desgs[item["title"]].id,
                        work_location="Headquarters",
                    )
                    db.add(emp)
                    await db.flush()
                seeded_employees[item["email"]] = emp
            print(f"  [OK] Users & Employees: {len(seeded_employees)} seeded")

            # 5. Attendance logs (Seed past 5 days for Rohit Employee)
            rohit = seeded_employees["employee@demo.hrgenie.ai"]
            today = date.today()
            attendance_count = 0
            for i in range(1, 6):
                log_date = today - timedelta(days=i)
                # Skip weekends
                if log_date.weekday() >= 5:
                    continue
                
                # Check if log already exists
                stmt = select(AttendanceLog).where(AttendanceLog.employee_id == rohit.id, AttendanceLog.date == log_date)
                log = (await db.execute(stmt)).scalar_one_or_none()
                if not log:
                    log = AttendanceLog(
                        employee_id=rohit.id,
                        date=log_date,
                        clock_in=datetime.combine(log_date, datetime.min.time().replace(hour=9), tzinfo=timezone.utc),
                        clock_out=datetime.combine(log_date, datetime.min.time().replace(hour=18), tzinfo=timezone.utc),
                        total_hours=9.0,
                        status=AttendanceStatus.present,
                    )
                    db.add(log)
                    attendance_count += 1
            await db.flush()
            print(f"  [OK] Attendance logs: {attendance_count} days seeded")

            # 6. Leave Types and Balances
            # LeaveType uses: name, code, annual_quota, is_paid, carry_forward
            leave_types = {}
            for name, code, annual_quota in [("Annual Leave", "AL", 18), ("Sick Leave", "SL", 8), ("Casual Leave", "CL", 6)]:
                stmt = select(LeaveType).where(LeaveType.company_id == company.id, LeaveType.name == name)
                lt = (await db.execute(stmt)).scalar_one_or_none()
                if not lt:
                    lt = LeaveType(
                        company_id=company.id,
                        name=name,
                        code=code,
                        annual_quota=annual_quota,
                    )
                    db.add(lt)
                    await db.flush()
                leave_types[name] = lt
            print(f"  [OK] Leave types: {list(leave_types.keys())}")

            # Seed balances for Rohit
            # LeaveBalance uses: employee_id, leave_type_id, year, allocated, used, pending
            for name, lt in leave_types.items():
                stmt = select(LeaveBalance).where(LeaveBalance.employee_id == rohit.id, LeaveBalance.leave_type_id == lt.id)
                bal = (await db.execute(stmt)).scalar_one_or_none()
                if not bal:
                    bal = LeaveBalance(
                        employee_id=rohit.id,
                        leave_type_id=lt.id,
                        year=today.year,
                        allocated=float(lt.annual_quota),
                        used=0,
                        pending=0,
                    )
                    db.add(bal)
            await db.flush()

            # Seed a pending leave request
            stmt = select(LeaveRequest).where(LeaveRequest.employee_id == rohit.id, LeaveRequest.status == LeaveStatus.pending)
            req = (await db.execute(stmt)).scalar_one_or_none()
            if not req:
                req = LeaveRequest(
                    employee_id=rohit.id,
                    leave_type_id=leave_types["Annual Leave"].id,
                    from_date=today + timedelta(days=5),
                    to_date=today + timedelta(days=7),
                    days_count=3.0,
                    reason="Family trip",
                    status=LeaveStatus.pending,
                )
                db.add(req)
            await db.flush()
            print(f"  [OK] Leave balances & requests seeded")

            # 7. Salary & Payroll
            # EmployeeSalary uses: employee_id, gross_salary, effective_from (no basic_pay, hra, etc.)
            for email, emp in seeded_employees.items():
                stmt = select(EmployeeSalary).where(EmployeeSalary.employee_id == emp.id)
                sal = (await db.execute(stmt)).scalar_one_or_none()
                if not sal:
                    sal = EmployeeSalary(
                        employee_id=emp.id,
                        gross_salary=Decimal("120000.00") if email == "admin@demo.hrgenie.ai" else Decimal("75000.00"),
                        effective_from=date(2026, 1, 1),
                    )
                    db.add(sal)
            await db.flush()
            print(f"  [OK] Employee salaries seeded")

            # Seed a computed payroll run for last month
            last_month_num = today.month - 1 or 12
            last_month_year = today.year if today.month - 1 > 0 else today.year - 1
            stmt = select(PayrollRun).where(
                PayrollRun.company_id == company.id,
                PayrollRun.month == last_month_num,
                PayrollRun.year == last_month_year
            )
            run = (await db.execute(stmt)).scalar_one_or_none()
            if not run:
                run = PayrollRun(
                    company_id=company.id,
                    month=last_month_num,
                    year=last_month_year,
                    status=PayrollStatus.approved,
                    total_gross=Decimal("270000.00"),
                    total_net=Decimal("240000.00"),
                )
                db.add(run)
                await db.flush()
            
            # Seed payroll entry for Rohit
            # PayrollEntry uses: payroll_run_id, employee_id, gross_salary, basic, hra, pf_deduction, esi_deduction, tds_deduction, lop_days, lop_deduction, net_salary
            stmt = select(PayrollEntry).where(PayrollEntry.payroll_run_id == run.id, PayrollEntry.employee_id == rohit.id)
            entry = (await db.execute(stmt)).scalar_one_or_none()
            if not entry:
                entry = PayrollEntry(
                    payroll_run_id=run.id,
                    employee_id=rohit.id,
                    gross_salary=Decimal("75000.00"),
                    basic=Decimal("37500.00"),
                    hra=Decimal("15000.00"),
                    pf_deduction=Decimal("4500.00"),
                    esi_deduction=Decimal("500.00"),
                    tds_deduction=Decimal("2500.00"),
                    lop_days=0,
                    lop_deduction=Decimal("0.00"),
                    net_salary=Decimal("67500.00"),
                )
                db.add(entry)
            await db.flush()
            print(f"  [OK] Payroll run & entry seeded")

            # 8. Performance Cycles & Goals
            stmt = select(PerformanceCycle).where(PerformanceCycle.company_id == company.id, PerformanceCycle.status == CycleStatus.active)
            cycle = (await db.execute(stmt)).scalar_one_or_none()
            if not cycle:
                cycle = PerformanceCycle(
                    company_id=company.id,
                    name="Q2 performance review",
                    cycle_type=CycleType.quarterly,
                    start_date=date(2026, 4, 1),
                    end_date=date(2026, 6, 30),
                    review_start=date(2026, 6, 15),
                    review_end=date(2026, 6, 30),
                    status=CycleStatus.active,
                )
                db.add(cycle)
                await db.flush()

            # Rohit Goal
            stmt = select(Goal).where(Goal.employee_id == rohit.id, Goal.cycle_id == cycle.id)
            goal = (await db.execute(stmt)).scalar_one_or_none()
            if not goal:
                goal = Goal(
                    company_id=company.id,
                    employee_id=rohit.id,
                    cycle_id=cycle.id,
                    title="Implement AI voice screening",
                    description="Integrate Whisper + Gemini to assess interview audio files.",
                    key_results=[
                        {"title": "Implement upload router", "target": 100, "unit": "%", "current": 100},
                        {"title": "Integrate Gemini grading", "target": 100, "unit": "%", "current": 80},
                    ],
                    weightage=30,
                    status=GoalStatus.in_progress,
                    due_date=date(2026, 6, 20),
                )
                db.add(goal)
            await db.flush()
            print(f"  [OK] Performance cycle & goals seeded")

            # 9. Job Postings & Applications
            # JobPosting uses: employment_type (string), salary_min, salary_max, requirements (text), description (text)
            stmt = select(JobPosting).where(JobPosting.company_id == company.id, JobPosting.title == "Lead Python Developer")
            job = (await db.execute(stmt)).scalar_one_or_none()
            if not job:
                job = JobPosting(
                    company_id=company.id,
                    title="Lead Python Developer",
                    department_id=depts["Engineering"].id,
                    location="Bengaluru",
                    employment_type="full_time",
                    salary_min=Decimal("1800000.00"),
                    salary_max=Decimal("2400000.00"),
                    openings_count=2,
                    deadline=date(2026, 8, 31),
                    status=JobStatus.open,
                    description="Looking for an expert Python developer to drive next-generation AI platforms.",
                    requirements="5+ years Python, FastAPI, SQLAlchemy 2.0",
                )
                db.add(job)
                await db.flush()

            # Candidate
            cand_email = "candidate@example.com"
            stmt = select(Candidate).where(Candidate.company_id == company.id, Candidate.email == cand_email)
            cand = (await db.execute(stmt)).scalar_one_or_none()
            if not cand:
                cand = Candidate(
                    company_id=company.id,
                    first_name="Amit",
                    last_name="Kumar",
                    email=cand_email,
                    phone="+91 88888 77777",
                )
                db.add(cand)
                await db.flush()

            # Application
            stmt = select(Application).where(Application.candidate_id == cand.id, Application.job_posting_id == job.id)
            app = (await db.execute(stmt)).scalar_one_or_none()
            if not app:
                app = Application(
                    candidate_id=cand.id,
                    job_posting_id=job.id,
                    stage=ApplicationStage.ai_screening,
                )
                db.add(app)
                await db.flush()

            # AI Evaluation
            stmt = select(AIEvaluation).where(AIEvaluation.application_id == app.id)
            eval_ai = (await db.execute(stmt)).scalar_one_or_none()
            if not eval_ai:
                eval_ai = AIEvaluation(
                    application_id=app.id,
                    fit_score=88,
                    skill_match_score=90,
                    experience_score=85,
                    overall_score=88,
                    strengths=["Excellent expertise in FastAPI", "Proficient in SQL tuning"],
                    weaknesses=["Lacks deep HuggingFace experience"],
                    ai_summary="Amit is an outstanding engineer displaying robust proficiency in FastAPI and database schemas. Highly recommended for the Lead Python Developer position.",
                    recommendation="Proceed to technical panel round",
                    confidence=0.92,
                )
                db.add(eval_ai)
            await db.flush()
            print(f"  [OK] Job posting, candidate, application & AI evaluation seeded")

            # 10. Notifications
            admin_stmt = select(User).where(User.email == "admin@demo.hrgenie.ai")
            admin_user = (await db.execute(admin_stmt)).scalar_one()
            rohit_stmt = select(User).where(User.email == "employee@demo.hrgenie.ai")
            rohit_user = (await db.execute(rohit_stmt)).scalar_one()
            
            notifications_data = [
                {
                    "user_id": admin_user.id,
                    "title": "Leave Request Pending",
                    "body": "Rohit Sharma has requested 3 days of Annual Leave.",
                    "category": "leave",
                },
                {
                    "user_id": admin_user.id,
                    "title": "New Candidate Application",
                    "body": "Amit Kumar has applied for Lead Python Developer.",
                    "category": "recruitment",
                },
                {
                    "user_id": admin_user.id,
                    "title": "Payroll Computed",
                    "body": "Payroll run for May 2026 has been computed.",
                    "category": "payroll",
                },
                {
                    "user_id": rohit_user.id,
                    "title": "Goal Assigned",
                    "body": "Q2 Performance Cycle goal 'Implement AI voice screening' has been assigned.",
                    "category": "performance",
                }
            ]

            notification_count = 0
            for item in notifications_data:
                stmt = select(Notification).where(
                    Notification.user_id == item["user_id"],
                    Notification.title == item["title"]
                )
                existing = (await db.execute(stmt)).scalar_one_or_none()
                if not existing:
                    notif = Notification(
                        user_id=item["user_id"],
                        title=item["title"],
                        body=item["body"],
                        category=item["category"],
                        is_read=False,
                    )
                    db.add(notif)
                    notification_count += 1
            await db.flush()
            print(f"  [OK] Notifications: {notification_count} seeded")

            await db.commit()
            print("\n[SUCCESS] Database demo data seeding finished successfully!")
            print("\n  Login credentials:")
            print("  -----------------------------------------")
            print("  Admin:    admin@demo.hrgenie.ai / Demo@1234")
            print("  HR:       hr@demo.hrgenie.ai / Demo@1234")
            print("  Manager:  manager@demo.hrgenie.ai / Demo@1234")
            print("  Employee: employee@demo.hrgenie.ai / Demo@1234")

        except Exception as e:
            await db.rollback()
            print(f"Error seeding database: {e}")
            import traceback
            traceback.print_exc()
            raise e

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: Database seeding execution failed: {e}")
        sys.exit(0)
