import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.recruitment import JobPosting, Application
from app.models.employee import Employee

async def main():
    async with AsyncSessionLocal() as db:
        job = (await db.execute(select(JobPosting))).scalars().first()
        app = (await db.execute(select(Application))).scalars().first()
        emp = (await db.execute(select(Employee))).scalars().first()
        print(f"JOB_ID={job.id if job else 'None'}")
        print(f"APP_ID={app.id if app else 'None'}")
        print(f"EMP_ID={emp.id if emp else 'None'}")

if __name__ == "__main__":
    asyncio.run(main())
