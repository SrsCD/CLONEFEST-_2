from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.core.deps import require_project_role
from app.models.project import ProjectMember
from app.models.bug import Bug
from app.models.enums import ProjectRole, BugStatus

router = APIRouter(prefix="/projects/{project_id}/stats", tags=["statistics"])


@router.get("")
def get_project_stats(
    project_id: int, db: Session = Depends(get_db),
    membership: ProjectMember = Depends(require_project_role(ProjectRole.VIEWER)),
):
    total = db.query(func.count(Bug.id)).filter(Bug.project_id == project_id).scalar()
    closed_statuses = [BugStatus.CLOSED, BugStatus.VERIFIED]
    open_count = db.query(func.count(Bug.id)).filter(
        Bug.project_id == project_id, ~Bug.status.in_(closed_statuses)
    ).scalar()
    closed_count = total - open_count

    def group_counts(column):
        rows = (
            db.query(column, func.count(Bug.id))
            .filter(Bug.project_id == project_id)
            .group_by(column)
            .all()
        )
        return {str(k.value if hasattr(k, "value") else k): v for k, v in rows}

    return {
        "total_bugs": total,
        "open_bugs": open_count,
        "closed_bugs": closed_count,
        "by_status": group_counts(Bug.status),
        "by_severity": group_counts(Bug.severity),
        "by_priority": group_counts(Bug.priority),
        "by_component": group_counts(Bug.component_id),
        "by_assignee": group_counts(Bug.assignee_id),
    }
