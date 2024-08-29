from typing import Annotated, Any

from fastapi import Depends
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import Task


class TaskFilter(Filter):
    order_by: list[str] | None = None
    status__ilike: str | None = None

    class Constants(Filter.Constants):
        model = Task


class TaskRepository:
    """This class implements the base interface for working with database."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
    ) -> None:
        self._session = session

    async def get(self, instance_id: int) -> Task | None:
        return await self._session.get(Task, instance_id)

    async def get_list(self, task_filter: TaskFilter, offset: int = 0, limit: int = 100) -> list[Task]:
        stmt = (
            select(Task)
            .offset(offset)
            .limit(limit)
        )
        stmt = task_filter.filter(stmt)
        query_result = await self._session.execute(stmt)

        return list(query_result.scalars().all())

    async def create(self, flush: bool = True) -> Task:
        instance = Task()
        self._session.add(instance)
        if flush:
            await self._session.flush()
            await self._session.refresh(instance)
        return instance

    async def update(
        self,
        task_id: int,
        validated_data: dict[str, Any],
        flush: bool = True,
    ) -> Task:
        task = await self.get(task_id)
        update_data = validated_data
        for column_name, column_value in update_data.items():
            setattr(task, column_name, column_value)
        self._session.add(task)
        if flush:
            await self._session.flush()
            await self._session.refresh(task)
        return task


TaskRepositoryDep = Annotated[TaskRepository, Depends(TaskRepository)]
