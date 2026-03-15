from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskStatus


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, task_id: UUID) -> Task | None:
        result = await self.db.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.assignee))
        )
        return result.scalar_one_or_none()

    async def list_for_project(self, project_id: UUID, status: TaskStatus | None = None) -> list[Task]:
        q = (
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.assignee))
            .order_by(Task.position, Task.created_at)
        )
        if status:
            q = q.where(Task.status == status)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def create(self, project_id: UUID, created_by_id: UUID, **kwargs) -> Task:
        task = Task(project_id=project_id, created_by_id=created_by_id, **kwargs)
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update(self, task: Task, **kwargs) -> Task:
        for key, value in kwargs.items():
            setattr(task, key, value)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.db.delete(task)
        await self.db.flush()
