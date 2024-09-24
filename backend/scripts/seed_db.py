"""Seed the database with initial users for testing."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed():
    async with SessionLocal() as session:
        async with engine.begin() as conn:
            await conn.run_sync(User.metadata.create_all)

        users = [
            User(username="admin", email="admin@hospital.org", hashed_password=get_password_hash("admin123"), role=UserRole.ADMIN),
            User(username="doctor1", email="doctor1@hospital.org", hashed_password=get_password_hash("doctor123"), role=UserRole.DOCTOR),
            User(username="doctor2", email="doctor2@hospital.org", hashed_password=get_password_hash("doctor123"), role=UserRole.DOCTOR),
            User(username="auditor", email="auditor@hospital.org", hashed_password=get_password_hash("auditor123"), role=UserRole.AUDITOR),
        ]
        for u in users:
            session.add(u)
        await session.commit()
        print("Seeded 4 users: admin/admin123, doctor1/doctor123, doctor2/doctor123, auditor/auditor123")


if __name__ == "__main__":
    asyncio.run(seed())
