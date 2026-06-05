"""Create all tables from SQLAlchemy models (bypasses Alembic migration)."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
# Import all models so Base.metadata knows about them
from app.models import *  # noqa

async def main():
    print("Creating all tables from models...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Done! All tables created successfully.")

if __name__ == "__main__":
    asyncio.run(main())
