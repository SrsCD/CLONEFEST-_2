from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.deps import require_project_role
from app.models.project import ProjectMember
from app.models.milestone import Milestone
from app.models.enums import ProjectRole
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate, MilestoneOut

router = APIRouter(prefix="/projects/{project_id}/milestones", tags=["milestones"])


@router.get("", response_model=list[MilestoneOut])
def list_milestones(
    project_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.VIEWER)),
):
    return db.query(Milestone).filter(Milestone.project_id == project_id).all()


@router.post("", response_model=MilestoneOut, status_code=status.HTTP_201_CREATED)
def create_milestone(
    project_id: int,
    payload: MilestoneCreate,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    milestone = Milestone(project_id=project_id, **payload.model_dump())
    db.add(milestone)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Milestone '{payload.name}' already exists in this project",
        )
    db.refresh(milestone)
    return milestone


@router.put("/{milestone_id}", response_model=MilestoneOut)
def update_milestone(
    project_id: int,
    milestone_id: int,
    payload: MilestoneUpdate,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    milestone = (
        db.query(Milestone)
        .filter(Milestone.id == milestone_id, Milestone.project_id == project_id)
        .first()
    )
    if milestone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)

    db.commit()
    db.refresh(milestone)
    return milestone


@router.delete("/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_milestone(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.ADMIN)),
):
    milestone = (
        db.query(Milestone)
        .filter(Milestone.id == milestone_id, Milestone.project_id == project_id)
        .first()
    )
    if milestone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    db.delete(milestone)
    db.commit()
    return None
