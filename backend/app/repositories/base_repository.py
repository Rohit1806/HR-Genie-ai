"""
Generic async CRUD repository with soft-delete support.
All queries are scoped by company_id when the model supports it.
"""

from typing import TypeVar, Generic, Type, Optional, Sequence
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, ColumnElement
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common CRUD operations for SQLAlchemy 2.0 async models."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    def _apply_soft_delete_filter(self, query):
        """Exclude soft-deleted rows when model supports deleted_at."""
        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))
        return query

    def _apply_company_scope(self, query, company_id: UUID | None):
        """Scope query to company when model has company_id column."""
        if company_id and hasattr(self.model, "company_id"):
            query = query.where(self.model.company_id == company_id)
        return query

    async def get_by_id(
        self, id: UUID, company_id: UUID | None = None
    ) -> ModelType | None:
        """Fetch a single record by primary key, scoped to company."""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_company_scope(query, company_id)
        query = self._apply_soft_delete_filter(query)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        company_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
        filters: list[ColumnElement] | None = None,
    ) -> tuple[Sequence[ModelType], int]:
        """
        List records with pagination and optional filters.
        Returns (items, total_count).
        """
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        query = self._apply_company_scope(query, company_id)
        count_query = self._apply_company_scope(count_query, company_id)

        query = self._apply_soft_delete_filter(query)
        count_query = self._apply_soft_delete_filter(count_query)

        if filters:
            for f in filters:
                query = query.where(f)
                count_query = count_query.where(f)

        total = (await self.session.execute(count_query)).scalar() or 0

        if hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all(), total

    async def create(self, **kwargs) -> ModelType:
        """Create a new record and flush to DB to obtain defaults."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(
        self, id: UUID, company_id: UUID | None = None, **kwargs
    ) -> ModelType | None:
        """
        Partial update — only non-None values are applied.
        Returns updated instance or None if not found.
        """
        instance = await self.get_by_id(id, company_id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def soft_delete(
        self, id: UUID, company_id: UUID | None = None
    ) -> bool:
        """Mark a record as deleted (soft delete). Returns True on success."""
        instance = await self.get_by_id(id, company_id)
        if not instance:
            return False
        if not hasattr(instance, "deleted_at"):
            return False
        instance.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def exists(
        self, id: UUID, company_id: UUID | None = None
    ) -> bool:
        """Check if a record exists."""
        instance = await self.get_by_id(id, company_id)
        return instance is not None

    async def count(
        self,
        company_id: UUID | None = None,
        filters: list[ColumnElement] | None = None,
    ) -> int:
        """Return total count of records matching filters."""
        query = select(func.count()).select_from(self.model)
        query = self._apply_company_scope(query, company_id)
        query = self._apply_soft_delete_filter(query)
        if filters:
            for f in filters:
                query = query.where(f)
        result = await self.session.execute(query)
        return result.scalar() or 0
