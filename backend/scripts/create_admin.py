"""
Admin provisioning script for HRGenie AI.
Creates default company, department, designation, admin user, and admin employee profile.
"""

import asyncio
import sys
from datetime import date
from uuid import uuid4

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
from app.models.employee import Employee, EmploymentType, EmploymentStatus


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        try:
            # 1. Look for or create default Company
            company_stmt = select(Company).where(Company.slug == "demo-company")
            res = await db.execute(company_stmt)
            company = res.scalar_one_or_none()

            if not company:
                company = Company(
                    name="Demo Company",
                    slug="demo-company",
                    timezone="Asia/Kolkata",
                    currency="INR",
                )
                db.add(company)
                await db.flush()
                print("Default company created successfully!")

            # 2. Look for or create default Department
            dept_stmt = select(Department).where(
                Department.company_id == company.id,
                Department.name == "Engineering",
            )
            res = await db.execute(dept_stmt)
            dept = res.scalar_one_or_none()

            if not dept:
                dept = Department(
                    company_id=company.id,
                    name="Engineering",
                )
                db.add(dept)
                await db.flush()
                print("Engineering department created successfully!")

            # 3. Look for or create default Designation
            desg_stmt = select(Designation).where(
                Designation.company_id == company.id,
                Designation.title == "Chief Technical Officer",
            )
            res = await db.execute(desg_stmt)
            desg = res.scalar_one_or_none()

            if not desg:
                desg = Designation(
                    company_id=company.id,
                    title="Chief Technical Officer",
                )
                db.add(desg)
                await db.flush()
                print("CTO designation created successfully!")

            # 4. Look for or create Admin User
            admin_email = "admin@demo.hrgenie.ai"
            user_stmt = select(User).where(
                User.company_id == company.id,
                User.email == admin_email,
            )
            res = await db.execute(user_stmt)
            admin_user = res.scalar_one_or_none()

            if not admin_user:
                admin_user = User(
                    company_id=company.id,
                    email=admin_email,
                    password_hash=hash_password("Demo@1234"),
                    full_name="System Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                db.add(admin_user)
                await db.flush()
                print("Admin user created successfully! Credentials: admin@demo.hrgenie.ai / Demo@1234")

            # 5. Look for or create Admin Employee profile
            emp_stmt = select(Employee).where(
                Employee.user_id == admin_user.id
            )
            res = await db.execute(emp_stmt)
            employee = res.scalar_one_or_none()

            if not employee:
                employee = Employee(
                    company_id=company.id,
                    user_id=admin_user.id,
                    employee_code="EMP001",
                    first_name="System",
                    last_name="Administrator",
                    date_of_birth=date(1990, 1, 1),
                    gender="male",
                    phone="+91 99999 88888",
                    personal_email=admin_email,
                    date_of_joining=date(2026, 1, 1),
                    employment_type=EmploymentType.full_time,
                    employment_status=EmploymentStatus.active,
                    department_id=dept.id,
                    designation_id=desg.id,
                    work_location="Headquarters",
                )
                db.add(employee)
                await db.flush()
                print("Admin employee profile created successfully!")

            await db.commit()
            print("Admin provisioning completed successfully with zero errors!")

        except Exception as e:
            await db.rollback()
            print(f"Error provisioning admin: {e}")
            raise e

if __name__ == "__main__":
    asyncio.run(main())
