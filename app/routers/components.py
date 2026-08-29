from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.deps import require_project_role
from app.models.project import ProjectMember
from app.models.component import Component
from app.models.enums import ProjectRole
from app.schemas.component import ComponentCreate, ComponentUpdate, ComponentOut

router = APIRouter(prefix="/projects/{project_id}/components", tags=["components"])


@router.get("", response_model=list[ComponentOut])
def list_components(
    project_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.VIEWER)),
):
    return db.query(Component).filter(Component.project_id == project_id).all()


@router.post("", response_model=ComponentOut, status_code=status.HTTP_201_CREATED)
def create_component(
    project_id: int,
    payload: ComponentCreate,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    component = Component(project_id=project_id, **payload.model_dump())
    db.add(component)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Component '{payload.name}' already exists in this project",
        )
    db.refresh(component)
    return component


@router.put("/{component_id}", response_model=ComponentOut)
def update_component(
    project_id: int,
    component_id: int,
    payload: ComponentUpdate,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    component = (
        db.query(Component)
        .filter(Component.id == component_id, Component.project_id == project_id)
        .first()
    )
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(component, field, value)

    db.commit()
    db.refresh(component)
    return component


@router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_component(
    project_id: int,
    component_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    component = (
        db.query(Component)
        .filter(Component.id == component_id, Component.project_id == project_id)
        .first()
    )
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")
    db.delete(component)
    db.commit()
    return None
