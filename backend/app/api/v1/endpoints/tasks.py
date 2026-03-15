from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, get_db, require_project_role
from app.models.membership import MemberRole
from app.repositories.task import TaskRepository
from app.schemas.project import TaskCreate, TaskRead, TaskUpdate
from app.services.websocket import manager

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
async def list_tasks(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = None,
):
    await require_project_role(project_id, current_user, db, MemberRole.VIEWER)
    repo = TaskRepository(db)
    from app.models.task import TaskStatus
    task_status = TaskStatus(status) if status else None
    return await repo.list_for_project(project_id, task_status)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: UUID,
    payload: TaskCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.MEMBER)
    repo = TaskRepository(db)
    task = await repo.create(
        project_id=project_id,
        created_by_id=current_user.id,
        **payload.model_dump(exclude_unset=True),
    )
    task_data = TaskRead.model_validate(task).model_dump(mode="json")
    await manager.broadcast(project_id, "task.created", task_data)
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    project_id: UUID,
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.VIEWER)
    repo = TaskRepository(db)
    task = await repo.get(task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    project_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.MEMBER)
    repo = TaskRepository(db)
    task = await repo.get(task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = await repo.update(task, **payload.model_dump(exclude_unset=True))
    task_data = TaskRead.model_validate(updated).model_dump(mode="json")
    await manager.broadcast(project_id, "task.updated", task_data)
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    project_id: UUID,
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.MEMBER)
    repo = TaskRepository(db)
    task = await repo.get(task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=404, detail="Task not found")
    await repo.delete(task)
    await manager.broadcast(project_id, "task.deleted", {"id": str(task_id)})
