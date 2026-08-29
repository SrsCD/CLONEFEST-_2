from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.deps import get_current_user, require_project_role
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.enums import ProjectRole
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectOut,
    ProjectMemberAdd,
    ProjectMemberRoleUpdate,
    ProjectMemberOut,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = Project(name=payload.name, key=payload.key, description=payload.description)
    db.add(project)
    try:
        db.flush()  # get project.id, still inside the transaction
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Project key '{payload.key}' is already in use"
        )

    # Creator becomes the first admin member — otherwise a brand-new
    # project would have zero members and nobody could manage it.
    db.add(ProjectMember(project_id=project.id, user_id=current_user.id, role=ProjectRole.ADMIN))
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectOut])
def list_my_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .filter(ProjectMember.user_id == current_user.id)
        .all()
    )


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.VIEWER)),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.is_archived is not None:
        project.is_archived = payload.is_archived

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_project(
    project_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    """
    Archives rather than hard-deletes — losing every bug in a project
    to one click is rarely what anyone actually wants. True hard-delete
    can be a separate, more guarded endpoint later if needed.
    """
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    project.is_archived = True
    db.commit()
    return None


# --- Members ---


@router.get("/{project_id}/members", response_model=list[ProjectMemberOut])
def list_members(
    project_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.VIEWER)),
):
    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()


@router.post("/{project_id}/members", response_model=ProjectMemberOut, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: int,
    payload: ProjectMemberAdd,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == payload.user_id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")

    member = ProjectMember(project_id=project_id, user_id=payload.user_id, role=payload.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.put("/{project_id}/members/{user_id}", response_model=ProjectMemberOut)
def update_member_role(
    project_id: int,
    user_id: int,
    payload: ProjectMemberRoleUpdate,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    member.role = payload.role
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    member = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    db.delete(member)
    db.commit()
    return None
