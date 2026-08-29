from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.deps import require_project_role
from app.models.project import ProjectMember
from app.models.label import Label
from app.models.enums import ProjectRole
from app.schemas.label import LabelCreate, LabelUpdate, LabelOut

router = APIRouter(prefix="/projects/{project_id}/labels", tags=["labels"])


@router.get("", response_model=list[LabelOut])
def list_labels(
    project_id: int, db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.VIEWER)),
):
    return db.query(Label).filter(Label.project_id == project_id).all()


@router.post("", response_model=LabelOut, status_code=status.HTTP_201_CREATED)
def create_label(
    project_id: int, payload: LabelCreate, db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    label = Label(project_id=project_id, **payload.model_dump())
    db.add(label)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail=f"Label '{payload.name}' already exists in this project")
    db.refresh(label)
    return label


@router.put("/{label_id}", response_model=LabelOut)
def update_label(
    project_id: int, label_id: int, payload: LabelUpdate, db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    label = db.query(Label).filter(Label.id == label_id, Label.project_id == project_id).first()
    if label is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(label, field, value)
    db.commit()
    db.refresh(label)
    return label


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_label(
    project_id: int, label_id: int, db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    label = db.query(Label).filter(Label.id == label_id, Label.project_id == project_id).first()
    if label is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    db.delete(label)
    db.commit()
    return None
