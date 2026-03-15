from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.models.membership import Membership, MemberRole
from app.repositories.user import UserRepository
from app.repositories.project import MembershipRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exc
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    repo = UserRepository(db)
    user = await repo.get(UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exc
    return user


async def require_project_role(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    min_role: MemberRole = MemberRole.VIEWER,
) -> Membership:
    repo = MembershipRepository(db)
    membership = await repo.get_by_user_and_project(current_user.id, project_id)

    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this project")

    role_hierarchy = {MemberRole.VIEWER: 0, MemberRole.MEMBER: 1, MemberRole.ADMIN: 2}
    if role_hierarchy[membership.role] < role_hierarchy[min_role]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return membership


CurrentUser = Annotated[User, Depends(get_current_user)]