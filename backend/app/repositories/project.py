from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.membership import Membership, MemberRole
from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, project_id: UUID) -> Project | None:
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID) -> list[Project]:
        result = await self.db.execute(
            select(Project)
            .join(Membership, Membership.project_id == Project.id)
            .where(Membership.user_id == user_id)
            .order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, name: str, owner_id: UUID, description: str | None = None) -> Project:
        project = Project(name=name, owner_id=owner_id, description=description)
        self.db.add(project)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def update(self, project: Project, **kwargs) -> Project:
        for key, value in kwargs.items():
            if value is not None:
                setattr(project, key, value)
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.db.delete(project)
        await self.db.flush()

    async def count_members(self, project_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(Membership.project_id == project_id)
        )
        return result.scalar_one()


class MembershipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_and_project(self, user_id: UUID, project_id: UUID) -> Membership | None:
        result = await self.db.execute(
            select(Membership).where(
                Membership.user_id == user_id,
                Membership.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_project(self, project_id: UUID) -> list[Membership]:
        result = await self.db.execute(
            select(Membership)
            .where(Membership.project_id == project_id)
            .options(selectinload(Membership.user))
            .order_by(Membership.joined_at)
        )
        return list(result.scalars().all())

    async def add(self, user_id: UUID, project_id: UUID, role: MemberRole) -> Membership:
        membership = Membership(user_id=user_id, project_id=project_id, role=role)
        self.db.add(membership)
        await self.db.flush()
        await self.db.refresh(membership)
        return membership

    async def remove(self, membership: Membership) -> None:
        await self.db.delete(membership)
        await self.db.flush()
