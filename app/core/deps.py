"""
Reusable FastAPI dependencies:
  - get_current_user: extracts + validates the JWT, loads the User
  - require_project_role: factory for "must be at least role X in this
    project" checks, used by any route nested under /projects/{project_id}
"""
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.project import ProjectMember
from app.models.enums import ProjectRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Role hierarchy — admin outranks developer outranks reporter outranks viewer.
# Used so "requires DEVELOPER" also lets an ADMIN through.
_ROLE_RANK = {
    ProjectRole.VIEWER: 0,
    ProjectRole.REPORTER: 1,
    ProjectRole.DEVELOPER: 2,
    ProjectRole.ADMIN: 3,
}


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_project_role(min_role: ProjectRole) -> Callable:
    """
    Returns a dependency that ensures the current user is a member of
    :project_id (a path param on the route) with at least `min_role`.

    Usage:
        @router.put("/projects/{project_id}")
        def update_project(
            project_id: int,
            membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
        ): ...
    """

    def dependency(
        project_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> ProjectMember:
        membership = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id,
            )
            .first()
        )
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project",
            )
        if _ROLE_RANK[membership.role] < _ROLE_RANK[min_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires at least '{min_role.value}' role in this project",
            )
        return membership

    return dependency


def check_membership(
    db: Session, user: User, project_id: int, min_role: ProjectRole
) -> ProjectMember:
    """
    Same check as require_project_role, but as a plain function — for
    routes keyed by bug_id (not project_id) that need to look the bug's
    project up first, then check access.
    """
    membership = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id)
        .first()
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this project"
        )
    if _ROLE_RANK[membership.role] < _ROLE_RANK[min_role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires at least '{min_role.value}' role in this project",
        )
    return membership
