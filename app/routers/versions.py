from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.deps import require_project_role
from app.models.project import ProjectMember
from app.models.version import Version
from app.models.enums import ProjectRole
from app.schemas.version import VersionCreate, VersionUpdate, VersionOut

router = APIRouter(prefix="/projects/{project_id}/versions", tags=["versions"])


@router.get("", response_model=list[VersionOut])
def list_versions(
    project_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.VIEWER)),
):
    return db.query(Version).filter(Version.project_id == project_id).all()


@router.post("", response_model=VersionOut, status_code=status.HTTP_201_CREATED)
def create_version(
    project_id: int,
    payload: VersionCreate,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    version = Version(project_id=project_id, **payload.model_dump())
    db.add(version)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version '{payload.name}' already exists in this project",
        )
    db.refresh(version)
    return version


@router.put("/{version_id}", response_model=VersionOut)
def update_version(
    project_id: int,
    version_id: int,
    payload: VersionUpdate,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    version = (
        db.query(Version).filter(Version.id == version_id, Version.project_id == project_id).first()
    )
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(version, field, value)

    db.commit()
    db.refresh(version)
    return version


@router.delete("/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_version(
    project_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    version = (
        db.query(Version).filter(Version.id == version_id, Version.project_id == project_id).first()
    )
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    db.delete(version)
    db.commit()
    return None
