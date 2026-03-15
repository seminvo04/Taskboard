from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, get_db, require_project_role
from app.models.membership import MemberRole
from app.repositories.project import MembershipRepository, ProjectRepository
from app.schemas.project import (
    MemberAdd,
    MemberRead,
    MemberUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectRead])
async def list_projects(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    repo = ProjectRepository(db)
    projects = await repo.list_for_user(current_user.id)
    result = []
    for p in projects:
        count = await repo.count_members(p.id)
        read = ProjectRead.model_validate(p)
        read.member_count = count
        result.append(read)
    return result


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_repo = ProjectRepository(db)
    member_repo = MembershipRepository(db)

    project = await project_repo.create(
        name=payload.name,
        owner_id=current_user.id,
        description=payload.description,
    )
    # Owner gets admin role automatically
    await member_repo.add(current_user.id, project.id, MemberRole.ADMIN)

    read = ProjectRead.model_validate(project)
    read.member_count = 1
    return read


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.VIEWER)
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    count = await repo.count_members(project_id)
    read = ProjectRead.model_validate(project)
    read.member_count = count
    return read


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.ADMIN)
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    updated = await repo.update(project, **payload.model_dump(exclude_unset=True))
    count = await repo.count_members(project_id)
    read = ProjectRead.model_validate(updated)
    read.member_count = count
    return read


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.ADMIN)
    repo = ProjectRepository(db)
    project = await repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can delete it")
    await repo.delete(project)


# ── Members ───────────────────────────────────────────────────────────────────

@router.get("/{project_id}/members", response_model=list[MemberRead])
async def list_members(
    project_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.VIEWER)
    repo = MembershipRepository(db)
    return await repo.list_for_project(project_id)


@router.post("/{project_id}/members", response_model=MemberRead, status_code=201)
async def add_member(
    project_id: UUID,
    payload: MemberAdd,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.ADMIN)
    repo = MembershipRepository(db)
    existing = await repo.get_by_user_and_project(payload.user_id, project_id)
    if existing:
        raise HTTPException(status_code=409, detail="User is already a member")
    membership = await repo.add(payload.user_id, project_id, payload.role)
    await db.refresh(membership, ["user"])
    return membership


@router.patch("/{project_id}/members/{user_id}", response_model=MemberRead)
async def update_member_role(
    project_id: UUID,
    user_id: UUID,
    payload: MemberUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.ADMIN)
    
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas modifier votre propre rôle")
    
    
    project_repo = ProjectRepository(db)
    project = await project_repo.get(project_id)
    if project and project.owner_id == user_id:
        raise HTTPException(status_code=403, detail="Impossible de modifier le rôle du propriétaire du projet")

    repo = MembershipRepository(db)
    membership = await repo.get_by_user_and_project(user_id, project_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membre introuvable")
    membership.role = payload.role
    await db.flush()
    await db.refresh(membership, ["user"])
    return membership


@router.delete("/{project_id}/members/{user_id}", status_code=204)
async def remove_member(
    project_id: UUID,
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_project_role(project_id, current_user, db, MemberRole.ADMIN)

    
    project_repo = ProjectRepository(db)
    project = await project_repo.get(project_id)
    if project and project.owner_id == user_id:
        raise HTTPException(status_code=403, detail="Impossible de retirer le propriétaire du projet")

    repo = MembershipRepository(db)
    membership = await repo.get_by_user_and_project(user_id, project_id)
    if not membership:
        raise HTTPException(status_code=404, detail="Membre introuvable")
    await repo.remove(membership)