import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

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
            dept_ids = {
                "Engineering": UUID("20ae9523-14d6-4363-b1ef-d7bc49655052"),
                "Human Resources": UUID("4c84b2f5-9bf2-41ac-ba26-457d87057fcb"),
                "Sales": UUID("77d83ff6-ee93-46ad-87a4-ba0df4400064"),
                "Finance": UUID("14ca5f0c-52fd-4cce-94c9-3d91f2a4ce03"),
            }
            depts = {}
            for dept_name in ["Engineering", "Human Resources", "Sales", "Finance"]:
                stmt = select(Department).where(Department.company_id == company.id, Department.name == dept_name)
                res = await db.execute(stmt)
                dept = res.scalar_one_or_none()
                if not dept:
                    dept = Department(id=dept_ids[dept_name], company_id=company.id, name=dept_name)
                    db.add(dept)
                    await db.flush()
                depts[dept_name] = dept
            print(f"  [OK] Departments: {list(depts.keys())}")

            # 3. Designations
            desg_ids = {
                "Chief Technical Officer": UUID("6666829e-cb67-4e16-bc4d-247cc5a551bd"),
                "Software Engineer": UUID("c8512f18-38c5-480b-ba86-05f595a21370"),
                "HR Director": UUID("2cc4a5da-933e-49a7-a62a-90281de58480"),
                "Talent Recruiter": UUID("78d723a6-329d-4133-93a2-988c7c3b0095"),
                "Sales Executive": UUID("9d4961a8-9315-4d89-9737-169c3a8b63bd"),
                "Finance Head": UUID("7a11b198-d260-4d6e-8ca1-8bc67536bcbf"),
            }
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
                    desg = Designation(id=desg_ids[title], company_id=company.id, title=title)
                    db.add(desg)
                    await db.flush()
                desgs[title] = desg
            print(f"  [OK] Designations: {list(desgs.keys())}")

            # 4. Users and Employees (15 Employees)
            employees_data = [
                {"email": "admin@demo.hrgenie.ai", "role": UserRole.ADMIN, "code": "EMP001", "first": "System", "last": "Administrator", "title": "Chief Technical Officer", "dept": "Engineering", "phone": "+91 99999 88888", "gender": "male"},
                {"email": "hr@demo.hrgenie.ai", "role": UserRole.HR_RECRUITER, "code": "EMP002", "first": "Sarah", "last": "Connor", "title": "HR Director", "dept": "Human Resources", "phone": "+91 99999 77777", "gender": "female"},
                {"email": "manager@demo.hrgenie.ai", "role": UserRole.SENIOR_MANAGER, "code": "EMP003", "first": "John", "last": "Manager", "title": "Finance Head", "dept": "Finance", "phone": "+91 99999 66666", "gender": "male"},
                {"email": "employee@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP004", "first": "Rohit", "last": "Sharma", "title": "Software Engineer", "dept": "Engineering", "phone": "+91 99999 55555", "gender": "male"},
                {"email": "emp5@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP005", "first": "Aman", "last": "Verma", "title": "Software Engineer", "dept": "Engineering", "phone": "+91 99999 44445", "gender": "male"},
                {"email": "emp6@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP006", "first": "Neha", "last": "Gupta", "title": "Software Engineer", "dept": "Engineering", "phone": "+91 99999 44446", "gender": "female"},
                {"email": "emp7@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP007", "first": "Rahul", "last": "Singh", "title": "Software Engineer", "dept": "Engineering", "phone": "+91 99999 44447", "gender": "male"},
                {"email": "emp8@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP008", "first": "Priya", "last": "Patel", "title": "Software Engineer", "dept": "Engineering", "phone": "+91 99999 44448", "gender": "female"},
                {"email": "emp9@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP009", "first": "Vikram", "last": "Rao", "title": "Talent Recruiter", "dept": "Human Resources", "phone": "+91 99999 44449", "gender": "male"},
                {"email": "emp10@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP010", "first": "Karan", "last": "Mehta", "title": "Talent Recruiter", "dept": "Human Resources", "phone": "+91 99999 44450", "gender": "male"},
                {"email": "emp11@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP011", "first": "Sanjay", "last": "Joshi", "title": "Sales Executive", "dept": "Sales", "phone": "+91 99999 44451", "gender": "male"},
                {"email": "emp12@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP012", "first": "Deepa", "last": "Nair", "title": "Sales Executive", "dept": "Sales", "phone": "+91 99999 44452", "gender": "female"},
                {"email": "emp13@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP013", "first": "Rohan", "last": "Das", "title": "Sales Executive", "dept": "Sales", "phone": "+91 99999 44453", "gender": "male"},
                {"email": "emp14@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP014", "first": "Anil", "last": "Kumar", "title": "Finance Head", "dept": "Finance", "phone": "+91 99999 44454", "gender": "male"},
                {"email": "emp15@demo.hrgenie.ai", "role": UserRole.EMPLOYEE, "code": "EMP015", "first": "Sunita", "last": "Sen", "title": "Finance Head", "dept": "Finance", "phone": "+91 99999 44455", "gender": "female"},
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
                        gender=item["gender"],
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

            # 5. Attendance logs (30 days of records for all 15 employees)
            today = date.today()
            attendance_count = 0
            for emp_email, emp in seeded_employees.items():
                days_added = 0
                day_offset = 1
                while days_added < 30:
                    log_date = today - timedelta(days=day_offset)
                    day_offset += 1
                    # Skip weekends
                    if log_date.weekday() >= 5:
                        continue
                    
                    # Check if log already exists
                    stmt = select(AttendanceLog).where(AttendanceLog.employee_id == emp.id, AttendanceLog.date == log_date)
                    log = (await db.execute(stmt)).scalar_one_or_none()
                    if not log:
                        log = AttendanceLog(
                            employee_id=emp.id,
                            date=log_date,
                            clock_in=datetime.combine(log_date, datetime.min.time().replace(hour=9), tzinfo=timezone.utc),
                            clock_out=datetime.combine(log_date, datetime.min.time().replace(hour=18), tzinfo=timezone.utc),
                            total_hours=9.0,
                            status=AttendanceStatus.present,
                        )
                        db.add(log)
                        attendance_count += 1
                    days_added += 1
            await db.flush()
            print(f"  [OK] Attendance logs: {attendance_count} records seeded (30 days per employee)")

            # 6. Leave Types
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

            # Seed balances for all employees
            for emp in seeded_employees.values():
                for name, lt in leave_types.items():
                    stmt = select(LeaveBalance).where(LeaveBalance.employee_id == emp.id, LeaveBalance.leave_type_id == lt.id)
                    bal = (await db.execute(stmt)).scalar_one_or_none()
                    if not bal:
                        bal = LeaveBalance(
                            employee_id=emp.id,
                            leave_type_id=lt.id,
                            year=today.year,
                            allocated=float(lt.annual_quota),
                            used=0,
                            pending=0,
                        )
                        db.add(bal)
            await db.flush()

            # Seed 5 leave requests in different statuses
            leave_requests_data = [
                {"email": "employee@demo.hrgenie.ai", "type": "Annual Leave", "days": 3.0, "reason": "Family trip", "status": LeaveStatus.pending, "offset": 5},
                {"email": "emp5@demo.hrgenie.ai", "type": "Sick Leave", "days": 2.0, "reason": "Flu recovery", "status": LeaveStatus.approved, "offset": -10},
                {"email": "emp6@demo.hrgenie.ai", "type": "Casual Leave", "days": 1.0, "reason": "Personal errand", "status": LeaveStatus.rejected, "offset": -5},
                {"email": "emp7@demo.hrgenie.ai", "type": "Annual Leave", "days": 5.0, "reason": "Summer vacation", "status": LeaveStatus.approved, "offset": -20},
                {"email": "emp8@demo.hrgenie.ai", "type": "Sick Leave", "days": 1.0, "reason": "Dental checkup", "status": LeaveStatus.pending, "offset": 8},
            ]

            leave_requests_count = 0
            for lr in leave_requests_data:
                emp = seeded_employees.get(lr["email"])
                if not emp:
                    continue
                
                from_date = today + timedelta(days=lr["offset"])
                to_date = from_date + timedelta(days=int(lr["days"]) - 1)
                
                stmt = select(LeaveRequest).where(
                    LeaveRequest.employee_id == emp.id,
                    LeaveRequest.from_date == from_date
                )
                req = (await db.execute(stmt)).scalar_one_or_none()
                if not req:
                    req = LeaveRequest(
                        employee_id=emp.id,
                        leave_type_id=leave_types[lr["type"]].id,
                        from_date=from_date,
                        to_date=to_date,
                        days_count=lr["days"],
                        reason=lr["reason"],
                        status=lr["status"],
                    )
                    db.add(req)
                    leave_requests_count += 1
            await db.flush()
            print(f"  [OK] Leave requests: {leave_requests_count} seeded in different statuses")

            # 7. Salaries & Payroll (3 months of data)
            # Create employee salary configurations
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

            # Seed 3 months of payroll runs & entries
            payroll_runs_data = [
                {"month": 3, "year": 2026},
                {"month": 4, "year": 2026},
                {"month": 5, "year": 2026},
            ]

            for pr in payroll_runs_data:
                stmt = select(PayrollRun).where(
                    PayrollRun.company_id == company.id,
                    PayrollRun.month == pr["month"],
                    PayrollRun.year == pr["year"]
                )
                run = (await db.execute(stmt)).scalar_one_or_none()
                if not run:
                    total_gross = Decimal("0.00")
                    total_net = Decimal("0.00")
                    run = PayrollRun(
                        company_id=company.id,
                        month=pr["month"],
                        year=pr["year"],
                        status=PayrollStatus.approved,
                        total_gross=total_gross,
                        total_net=total_net,
                    )
                    db.add(run)
                    await db.flush()

                # For each employee, create payroll entry for this run
                for email, emp in seeded_employees.items():
                    stmt = select(PayrollEntry).where(
                        PayrollEntry.payroll_run_id == run.id,
                        PayrollEntry.employee_id == emp.id
                    )
                    entry = (await db.execute(stmt)).scalar_one_or_none()
                    if not entry:
                        gross = Decimal("120000.00") if email == "admin@demo.hrgenie.ai" else Decimal("75000.00")
                        basic = gross * Decimal("0.50")
                        hra = gross * Decimal("0.20")
                        pf = gross * Decimal("0.06")
                        esi = gross * Decimal("0.006")
                        tds = gross * Decimal("0.033")
                        net = gross - pf - esi - tds
                        
                        entry = PayrollEntry(
                            payroll_run_id=run.id,
                            employee_id=emp.id,
                            gross_salary=gross,
                            basic=basic,
                            hra=hra,
                            pf_deduction=pf,
                            esi_deduction=esi,
                            tds_deduction=tds,
                            lop_days=0,
                            lop_deduction=Decimal("0.00"),
                            net_salary=net,
                        )
                        db.add(entry)
                        
                        run.total_gross += gross
                        run.total_net += net
                        db.add(run)
                await db.flush()
            print(f"  [OK] Payroll: 3 months of runs and entries seeded for all 15 employees")

            # 8. Performance Cycles & Goals (5 goals per employee)
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

            goals_data_templates = [
                {"title": "Core Deliverables & Quality", "desc": "Design, implement and verify the core module requirements.", "krs": [{"title": "Complete code implementation", "target": 100, "unit": "%", "current": 90}, {"title": "Coverage above 80%", "target": 80, "unit": "%", "current": 75}]},
                {"title": "System Performance Optimization", "desc": "Reduce query and endpoint latencies.", "krs": [{"title": "API average latency < 200ms", "target": 200, "unit": "ms", "current": 250}]},
                {"title": "Documentation & Onboarding", "desc": "Write comprehensive internal documentation.", "krs": [{"title": "Write 5 code design docs", "target": 5, "unit": "docs", "current": 4}]},
                {"title": "Team Mentoring & Collaboration", "desc": "Help train and onboard junior developers.", "krs": [{"title": "Conduct 3 code review walkthroughs", "target": 3, "unit": "sessions", "current": 2}]},
                {"title": "Professional Development", "desc": "Participate in AI-assisted coding courses.", "krs": [{"title": "Complete 1 external training module", "target": 1, "unit": "course", "current": 1}]},
            ]

            goals_seeded = 0
            for emp in seeded_employees.values():
                for idx, template in enumerate(goals_data_templates):
                    stmt = select(Goal).where(
                        Goal.employee_id == emp.id,
                        Goal.cycle_id == cycle.id,
                        Goal.title == template["title"]
                    )
                    goal = (await db.execute(stmt)).scalar_one_or_none()
                    if not goal:
                        goal = Goal(
                            company_id=company.id,
                            employee_id=emp.id,
                            cycle_id=cycle.id,
                            title=template["title"],
                            description=template["desc"],
                            key_results=template["krs"],
                            weightage=20,
                            status=GoalStatus.in_progress,
                            due_date=date(2026, 6, 30),
                        )
                        db.add(goal)
                        goals_seeded += 1
            await db.flush()
            print(f"  [OK] Performance goals: {goals_seeded} goals seeded (5 per employee)")

            # 9. Job Postings, Candidates, Applications & AI Evaluations
            job_postings_data = [
                {
                    "title": "Lead Python Developer",
                    "dept": "Engineering",
                    "desc": "Looking for an expert Python developer to drive next-generation AI platforms.",
                    "reqs": "5+ years Python, FastAPI, SQLAlchemy 2.0",
                },
                {
                    "title": "Senior HR Specialist",
                    "dept": "Human Resources",
                    "desc": "HR leader to manage talent development programs.",
                    "reqs": "4+ years HR management, HRIS databases",
                },
                {
                    "title": "Senior Frontend React Engineer",
                    "dept": "Engineering",
                    "desc": "Frontend engineer to build vibrant, responsive user interfaces.",
                    "reqs": "3+ years React, TypeScript, TailwindCSS",
                }
            ]

            seeded_jobs = []
            for jp in job_postings_data:
                stmt = select(JobPosting).where(JobPosting.company_id == company.id, JobPosting.title == jp["title"])
                job = (await db.execute(stmt)).scalar_one_or_none()
                if not job:
                    job = JobPosting(
                        company_id=company.id,
                        title=jp["title"],
                        department_id=depts[jp["dept"]].id,
                        location="Bengaluru",
                        employment_type="full_time",
                        salary_min=Decimal("1500000.00"),
                        salary_max=Decimal("2500000.00"),
                        openings_count=2,
                        deadline=date(2026, 8, 31),
                        status=JobStatus.open,
                        description=jp["desc"],
                        requirements=jp["reqs"],
                    )
                    db.add(job)
                    await db.flush()
                seeded_jobs.append(job)

            # Seed 5 candidates per job posting (15 candidates total)
            candidates_count = 0
            applications_count = 0
            evaluations_count = 0
            
            python_candidates_data = [
                {
                    "first_name": "Alex",
                    "last_name": "Carter",
                    "email": "alex.carter@demo.hrgenie.ai",
                    "phone": "+91 99999 10001",
                    "stage": ApplicationStage.applied,
                    "resume_text": """ALEX CARTER\nLead Python Developer\nEmail: alex.carter@demo.hrgenie.ai | Phone: +91 99999 10001\n\nSUMMARY:\nHighly skilled Lead Backend Engineer with 8+ years of experience designing and scaling web applications, microservices, and AI-driven platforms. Expert in Python, FastAPI, Django, and SQLAlchemy.\n\nTECHNICAL SKILLS:\n- Languages: Python, SQL, JavaScript, Bash\n- Frameworks: FastAPI, Django, Flask, PyTest\n- Databases: PostgreSQL, Redis, MongoDB, SQLAlchemy 2.0\n- DevOps & Tools: Docker, Kubernetes, AWS (S3, EC2, ECS), Git, GitHub Actions, Celery\n\nEXPERIENCE:\nLead Backend Engineer | TechVantage Solutions (2023 - Present)\n- Designed and built scalable backend APIs using FastAPI and SQLAlchemy 2.0, improving request throughput by 45%.\n- Integrated LLMs and AI pipelines into core business flows.\n- Led a team of 4 software engineers in development of microservice architecture.\n\nSenior Software Engineer | CloudScale Systems (2020 - 2023)\n- Implemented high-performance data processing pipelines using Python, Celery, and Redis.\n- Optimized slow SQL queries and database indexes, reducing query response times by 30%.\n- Set up automated CI/CD pipelines using GitHub Actions and Docker.\n\nEDUCATION:\nBachelor of Technology in Computer Science | Delhi Technological University (2016)""",
                    "eval": {
                        "fit_score": 90.0,
                        "skill_match_score": 92.0,
                        "experience_score": 88.0,
                        "overall_score": 90.0,
                        "strengths": ["8+ years python experience", "Expert in FastAPI and SQLAlchemy 2.0", "DevOps and cloud deployment expertise"],
                        "weaknesses": ["None identified for this senior level"],
                        "ai_summary": "Alex Carter is an outstanding Lead Python Developer candidate. He matches all core technical requirements, has significant team leadership experience, and has previously built next-gen AI platform APIs.",
                        "recommendation": "STRONG_YES",
                        "confidence": 0.95
                    }
                },
                {
                    "first_name": "Sarah",
                    "last_name": "Jenkins",
                    "email": "sarah.jenkins@demo.hrgenie.ai",
                    "phone": "+91 99999 10002",
                    "stage": ApplicationStage.ai_screening,
                    "resume_text": """SARAH JENKINS\nSenior Python Engineer\nEmail: sarah.jenkins@demo.hrgenie.ai | Phone: +91 99999 10002\n\nSUMMARY:\nSenior Software Engineer with 6+ years of professional backend development experience using Python. Passionate about building robust web applications, optimizing databases, and setting up automated testing frameworks.\n\nTECHNICAL SKILLS:\n- Backend: Python, FastAPI, Django, Celery\n- Databases: PostgreSQL, SQLite, Redis, SQLAlchemy\n- Testing: Pytest, Unittest, Mocking\n- Tools: Docker, Git, GitLab CI, AWS\n\nEXPERIENCE:\nSenior Python Developer | InnovateTech Inc. (2022 - Present)\n- Developed and maintained FastAPI and Django REST APIs for high-traffic financial applications.\n- Migrated legacy SQLAlchemy queries to SQLAlchemy 2.0, reducing latency.\n- Refactored test suites to achieve 90% test coverage using Pytest.\n\nSoftware Engineer | CodeCraft Studios (2020 - 2022)\n- Built internal tooling and data scraping systems in Python.\n- Maintained PostgreSQL databases and wrote complex analytical SQL queries.\n\nEDUCATION:\nB.S. in Computer Science | Birla Institute of Technology and Science (2019)""",
                    "eval": {
                        "fit_score": 82.0,
                        "skill_match_score": 85.0,
                        "experience_score": 80.0,
                        "overall_score": 82.0,
                        "strengths": ["Strong FastAPI and SQLAlchemy skills", "Excellent focus on unit testing and CI/CD", "Solid PostgreSQL experience"],
                        "weaknesses": ["Limited experience leading large engineering projects"],
                        "ai_summary": "Sarah Jenkins shows high capability as a Senior Python Engineer. Her skills align perfectly with the backend stack, especially FastAPI and SQLAlchemy. Recommended for technical review.",
                        "recommendation": "YES",
                        "confidence": 0.90
                    }
                },
                {
                    "first_name": "Priya",
                    "last_name": "Sharma",
                    "email": "priya.sharma@demo.hrgenie.ai",
                    "phone": "+91 99999 10003",
                    "stage": ApplicationStage.shortlisted,
                    "resume_text": """PRIYA SHARMA\nBackend Developer\nEmail: priya.sharma@demo.hrgenie.ai | Phone: +91 99999 10003\n\nSUMMARY:\nBackend Engineer with 4 years of experience focusing on Python web frameworks and API design. Eager to grow into lead-level roles and work with next-gen AI integrations.\n\nTECHNICAL SKILLS:\n- Languages: Python, SQL, Java\n- Frameworks: Django, Flask, FastAPI\n- Databases: MySQL, PostgreSQL, Redis, MongoDB\n- Tools: Git, Docker, AWS (S3, RDS)\n\nEXPERIENCE:\nSoftware Engineer | Enterprise Softwares (2022 - Present)\n- Designed and documented REST APIs for enterprise clients using Django and Flask.\n- Integrated third-party payment gateways and notification APIs.\n- Collaborated with frontend teams to optimize API payloads.\n\nJunior Backend Developer | TechStart Systems (2020 - 2022)\n- Maintained Python-based scrapers and legacy Django scripts.\n- Assisted in database migration tasks.\n\nEDUCATION:\nBachelor of Engineering in IT | Pune University (2020)""",
                    "eval": {
                        "fit_score": 70.0,
                        "skill_match_score": 75.0,
                        "experience_score": 60.0,
                        "overall_score": 70.0,
                        "strengths": ["Good Python foundations", "Familiarity with multiple web frameworks (Django, Flask, FastAPI)", "Enthusiastic to learn"],
                        "weaknesses": ["Under-experienced for a lead role (4 years vs 5+ required)", "Limited experience with SQLAlchemy 2.0 and async Python"],
                        "ai_summary": "Priya Sharma is a solid backend engineer, but might be slightly junior for a Lead role. Her skills in REST APIs and database integrations are strong and make her a good candidate for standard backend roles.",
                        "recommendation": "MAYBE",
                        "confidence": 0.85
                    }
                },
                {
                    "first_name": "David",
                    "last_name": "Vance",
                    "email": "david.vance@demo.hrgenie.ai",
                    "phone": "+91 99999 10004",
                    "stage": ApplicationStage.interview,
                    "resume_text": """DAVID VANCE\nBackend Engineer\nEmail: david.vance@demo.hrgenie.ai | Phone: +91 99999 10004\n\nSUMMARY:\nSoftware Developer with 3 years of experience. Experienced in building Python web services, writing automated tests, and working with SQL databases.\n\nTECHNICAL SKILLS:\n- Python, Django, REST APIs, Git, PostgreSQL, Docker, AWS\n\nEXPERIENCE:\nPython Developer | AppForge Co. (2023 - Present)\n- Created backend APIs using Python and Django.\n- Handled PostgreSQL schema updates and optimization.\n\nJunior Developer | WebCrafters (2021 - 2023)\n- Supported development of web applications.\n\nEDUCATION:\nB.Tech in Computer Science | Amity University (2021)""",
                    "eval": {
                        "fit_score": 55.0,
                        "skill_match_score": 60.0,
                        "experience_score": 45.0,
                        "overall_score": 55.0,
                        "strengths": ["Clear communication and clean code habits", "Solid SQL foundations"],
                        "weaknesses": ["Significantly below the experience requirement (3 years)", "No professional exposure to FastAPI or SQLAlchemy 2.0"],
                        "ai_summary": "David Vance is a promising developer but currently lacks the necessary years of experience and core framework exposure (FastAPI/SQLAlchemy 2.0) needed for a Lead position.",
                        "recommendation": "NO",
                        "confidence": 0.80
                    }
                },
                {
                    "first_name": "Emily",
                    "last_name": "Watson",
                    "email": "emily.watson@demo.hrgenie.ai",
                    "phone": "+91 99999 10005",
                    "stage": ApplicationStage.technical,
                    "resume_text": """EMILY WATSON\nSenior Backend & AI Engineer\nEmail: emily.watson@demo.hrgenie.ai | Phone: +91 99999 10005\n\nSUMMARY:\nSenior Engineer with 7+ years of experience specializing in Python backends, high-performance computing, and AI/ML model deployment. Expert in FastAPI, SQLAlchemy, and cloud platforms.\n\nTECHNICAL SKILLS:\n- Languages: Python, C++, SQL, Go\n- Web Stack: FastAPI, SQLAlchemy 2.0, Redis, Docker, Kubernetes\n- ML/AI: PyTorch, HuggingFace, Model Optimization, Vector Databases\n- Cloud: AWS, Google Cloud, Terraform, GitHub Actions\n\nEXPERIENCE:\nSenior AI Backend Engineer | DeepCloud Labs (2023 - Present)\n- Architected next-generation AI platforms using FastAPI, serving millions of inference calls.\n- Designed vector database schemas using pgvector and Qdrant for semantic search engines.\n- Built async database layer using SQLAlchemy 2.0, reducing average API response to 40ms.\n\nSenior Backend Developer | FutureFlow Tech (2019 - 2023)\n- Scaled backend web services using Python and Go.\n- Led migration of on-prem systems to AWS using Terraform.\n\nEDUCATION:\nMaster of Science in Computer Science | IIT Bombay (2019)""",
                    "eval": {
                        "fit_score": 93.0,
                        "skill_match_score": 95.0,
                        "experience_score": 90.0,
                        "overall_score": 93.0,
                        "strengths": ["Exceptional FastAPI and SQLAlchemy 2.0 expertise", "Deep AI/ML model deployment & vector DB experience", "Strong architectural background"],
                        "weaknesses": ["None"],
                        "ai_summary": "Emily Watson is an outstanding fit for the Lead Python Developer position, especially given our focus on next-gen AI platforms. She has immediate, direct experience with FastAPI, async SQLAlchemy 2.0, and pgvector.",
                        "recommendation": "STRONG_YES",
                        "confidence": 0.98
                    }
                }
            ]

            for job_idx, job in enumerate(seeded_jobs):
                if job.title == "Lead Python Developer":
                    for cand_data in python_candidates_data:
                        stmt = select(Candidate).where(Candidate.company_id == company.id, Candidate.email == cand_data["email"])
                        cand = (await db.execute(stmt)).scalar_one_or_none()
                        if not cand:
                            cand = Candidate(
                                company_id=company.id,
                                first_name=cand_data["first_name"],
                                last_name=cand_data["last_name"],
                                email=cand_data["email"],
                                phone=cand_data["phone"],
                                resume_text=cand_data["resume_text"],
                            )
                            db.add(cand)
                            await db.flush()
                            candidates_count += 1
                        else:
                            cand.resume_text = cand_data["resume_text"]
                            db.add(cand)

                        # Application
                        stmt = select(Application).where(Application.candidate_id == cand.id, Application.job_posting_id == job.id)
                        app = (await db.execute(stmt)).scalar_one_or_none()
                        if not app:
                            app = Application(
                                candidate_id=cand.id,
                                job_posting_id=job.id,
                                stage=cand_data["stage"],
                            )
                            db.add(app)
                            await db.flush()
                            applications_count += 1
                        else:
                            app.stage = cand_data["stage"]
                            db.add(app)

                        # AI Evaluation
                        stmt = select(AIEvaluation).where(AIEvaluation.application_id == app.id)
                        eval_ai = (await db.execute(stmt)).scalar_one_or_none()
                        if not eval_ai:
                            eval_ai = AIEvaluation(
                                application_id=app.id,
                                fit_score=cand_data["eval"]["fit_score"],
                                skill_match_score=cand_data["eval"]["skill_match_score"],
                                experience_score=cand_data["eval"]["experience_score"],
                                overall_score=cand_data["eval"]["overall_score"],
                                strengths=cand_data["eval"]["strengths"],
                                weaknesses=cand_data["eval"]["weaknesses"],
                                ai_summary=cand_data["eval"]["ai_summary"],
                                recommendation=cand_data["eval"]["recommendation"],
                                confidence=cand_data["eval"]["confidence"],
                            )
                            db.add(eval_ai)
                            evaluations_count += 1
                        else:
                            eval_ai.fit_score=cand_data["eval"]["fit_score"]
                            eval_ai.skill_match_score=cand_data["eval"]["skill_match_score"]
                            eval_ai.experience_score=cand_data["eval"]["experience_score"]
                            eval_ai.overall_score=cand_data["eval"]["overall_score"]
                            eval_ai.strengths=cand_data["eval"]["strengths"]
                            eval_ai.weaknesses=cand_data["eval"]["weaknesses"]
                            eval_ai.ai_summary=cand_data["eval"]["ai_summary"]
                            eval_ai.recommendation=cand_data["eval"]["recommendation"]
                            eval_ai.confidence=cand_data["eval"]["confidence"]
                            db.add(eval_ai)
                else:
                    for cand_idx in range(1, 6):
                        cand_email = f"candidate_{job_idx}_{cand_idx}@example.com"
                        stmt = select(Candidate).where(Candidate.company_id == company.id, Candidate.email == cand_email)
                        cand = (await db.execute(stmt)).scalar_one_or_none()
                        if not cand:
                            cand = Candidate(
                                company_id=company.id,
                                first_name=f"Applicant {cand_idx}",
                                last_name=f"Job {job_idx + 1}",
                                email=cand_email,
                                phone=f"+91 88888 111{job_idx}{cand_idx}",
                            )
                            db.add(cand)
                            await db.flush()
                            candidates_count += 1

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
                            applications_count += 1

                        # AI Evaluation
                        stmt = select(AIEvaluation).where(AIEvaluation.application_id == app.id)
                        eval_ai = (await db.execute(stmt)).scalar_one_or_none()
                        if not eval_ai:
                            fit_score = 70 + (cand_idx * 5) % 30
                            eval_ai = AIEvaluation(
                                application_id=app.id,
                                fit_score=fit_score,
                                skill_match_score=fit_score + 2,
                                experience_score=fit_score - 4,
                                overall_score=fit_score,
                                strengths=["Fast learner", "Excellent technical background"],
                                weaknesses=["Limited domain experience"],
                                ai_summary=f"Candidate displays strong technical capabilities. Highly matched for the {job.title} position.",
                                recommendation="Proceed to technical round",
                                confidence=0.90,
                            )
                            db.add(eval_ai)
                            evaluations_count += 1
            await db.flush()
            print(f"  [OK] Recruitment: {len(seeded_jobs)} jobs, {candidates_count} candidates, {applications_count} applications, and {evaluations_count} AI evaluations seeded")

            # 10. Notifications
            admin_stmt = select(User).where(User.email == "admin@demo.hrgenie.ai")
            admin_user = (await db.execute(admin_stmt)).scalar_one()
            rohit_stmt = select(User).where(User.email == "employee@demo.hrgenie.ai")
            rohit_user = (await db.execute(rohit_stmt)).scalar_one()
            
            notifications_data = [
                {"user_id": admin_user.id, "title": "Leave Request Pending", "body": "Rohit Sharma has requested 3 days of Annual Leave.", "category": "leave"},
                {"user_id": admin_user.id, "title": "New Candidate Application", "body": "Candidate has applied for Lead Python Developer.", "category": "recruitment"},
                {"user_id": admin_user.id, "title": "Payroll Computed", "body": "Payroll run for May 2026 has been computed.", "category": "payroll"},
                {"user_id": rohit_user.id, "title": "Goal Assigned", "body": "Q2 Performance Cycle goal has been assigned.", "category": "performance"},
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
