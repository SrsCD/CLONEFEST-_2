"""
The main bug-management router. Deliberately kept as one file since
everything here revolves around a single Bug row and its related
sub-resources (comments, attachments, labels, relationships, history) —
splitting further would just mean importing Bug + check_membership +
history-logging helpers into five separate files.
"""
import os
import shutil
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.core.deps import get_current_user, check_membership
from app.models.user import User
from app.models.bug import Bug
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.label import Label
from app.models.history import BugHistory
from app.models.relationship import BugRelationship
from app.models.notification import Notification
from app.models.enums import (
    ProjectRole,
    BugStatus,
    HistoryActionType,
    NotificationType,
    ALLOWED_STATUS_TRANSITIONS,
)
from app.schemas.bug import BugCreate, BugUpdate, BugOut
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut
from app.schemas.attachment import AttachmentOut
from app.schemas.relationship import RelationshipCreate, RelationshipOut, BugDependencies
from app.schemas.history import BugHistoryOut

router = APIRouter(prefix="/bugs", tags=["bugs"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")


def _get_bug_or_404(db: Session, bug_id: int) -> Bug:
    bug = db.get(Bug, bug_id)
    if bug is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bug not found")
    return bug


def _log_history(
    db: Session, bug_id: int, user_id: int, action: HistoryActionType,
    field_name: Optional[str] = None, old_value: Optional[str] = None, new_value: Optional[str] = None,
):
    db.add(BugHistory(
        bug_id=bug_id, changed_by_id=user_id, action_type=action,
        field_name=field_name, old_value=old_value, new_value=new_value,
    ))


def _notify(db: Session, user_id: int, ntype: NotificationType, message: str, bug_id: int, project_id: int):
    db.add(Notification(
        user_id=user_id, type=ntype, message=message, bug_id=bug_id, project_id=project_id,
    ))


# --- Create / list / search / get / update / delete ---


@router.post("", response_model=BugOut, status_code=status.HTTP_201_CREATED)
def create_bug(
    project_id: int,
    payload: BugCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_membership(db, current_user, project_id, ProjectRole.REPORTER)

    bug = Bug(
        project_id=project_id,
        reporter_id=current_user.id,
        **payload.model_dump(exclude={"label_ids"}),
    )
    if payload.label_ids:
        bug.labels = db.query(Label).filter(
            Label.id.in_(payload.label_ids), Label.project_id == project_id
        ).all()

    db.add(bug)
    db.flush()
    _log_history(db, bug.id, current_user.id, HistoryActionType.CREATED)

    if bug.assignee_id and bug.assignee_id != current_user.id:
        _notify(db, bug.assignee_id, NotificationType.ASSIGNED,
                f"You were assigned to bug #{bug.id}: {bug.title}", bug.id, project_id)

    db.commit()
    db.refresh(bug)
    return bug


@router.get("/search", response_model=list[BugOut])
def search_bugs(
    project_id: int,
    status_filter: Optional[BugStatus] = None,
    severity: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    reporter_id: Optional[int] = None,
    component_id: Optional[int] = None,
    version_id: Optional[int] = None,
    milestone_id: Optional[int] = None,
    is_security: Optional[bool] = None,
    q: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Combinable filters, e.g. status=in_progress&severity=critical&assignee_id=3."""
    check_membership(db, current_user, project_id, ProjectRole.VIEWER)

    query = db.query(Bug).filter(Bug.project_id == project_id)
    if status_filter is not None:
        query = query.filter(Bug.status == status_filter)
    if severity is not None:
        query = query.filter(Bug.severity == severity)
    if priority is not None:
        query = query.filter(Bug.priority == priority)
    if assignee_id is not None:
        query = query.filter(Bug.assignee_id == assignee_id)
    if reporter_id is not None:
        query = query.filter(Bug.reporter_id == reporter_id)
    if component_id is not None:
        query = query.filter(Bug.component_id == component_id)
    if version_id is not None:
        query = query.filter(Bug.version_id == version_id)
    if milestone_id is not None:
        query = query.filter(Bug.milestone_id == milestone_id)
    if is_security is not None:
        query = query.filter(Bug.is_security == is_security)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Bug.title.ilike(like), Bug.description.ilike(like)))

    return query.order_by(Bug.id.desc()).all()


@router.get("", response_model=list[BugOut])
def list_bugs(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_membership(db, current_user, project_id, ProjectRole.VIEWER)
    return db.query(Bug).filter(Bug.project_id == project_id).order_by(Bug.id.desc()).all()


@router.get("/{bug_id}", response_model=BugOut)
def get_bug(bug_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.VIEWER)
    return bug


@router.put("/{bug_id}", response_model=BugOut)
def update_bug(
    bug_id: int,
    payload: BugUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.DEVELOPER)

    changes = payload.model_dump(exclude_unset=True)

    # Validate status transition before applying anything.
    if "status" in changes and changes["status"] != bug.status:
        new_status = changes["status"]
        allowed = ALLOWED_STATUS_TRANSITIONS.get(bug.status, set())
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition bug from '{bug.status.value}' to '{new_status.value}'",
            )

    # Apply changes, logging history for the fields that matter most.
    for field, new_value in changes.items():
        old_value = getattr(bug, field)
        if old_value == new_value:
            continue
        setattr(bug, field, new_value)

        if field == "status":
            _log_history(db, bug.id, current_user.id, HistoryActionType.STATUS_CHANGED,
                         "status", str(old_value.value), str(new_value.value))
            if new_value == BugStatus.REOPENED:
                _log_history(db, bug.id, current_user.id, HistoryActionType.REOPENED)
            if new_value == BugStatus.RESOLVED:
                from datetime import datetime, timezone
                bug.resolved_at = datetime.now(timezone.utc)
                _notify(db, bug.reporter_id, NotificationType.RESOLVED,
                        f"Bug #{bug.id} was marked resolved: {bug.title}", bug.id, bug.project_id)
            if new_value == BugStatus.CLOSED:
                from datetime import datetime, timezone
                bug.closed_at = datetime.now(timezone.utc)
        elif field == "priority":
            _log_history(db, bug.id, current_user.id, HistoryActionType.PRIORITY_CHANGED,
                         "priority", str(old_value.value), str(new_value.value))
        elif field == "severity":
            _log_history(db, bug.id, current_user.id, HistoryActionType.SEVERITY_CHANGED,
                         "severity", str(old_value.value), str(new_value.value))
        elif field == "assignee_id":
            _log_history(db, bug.id, current_user.id, HistoryActionType.ASSIGNEE_CHANGED,
                         "assignee_id", str(old_value), str(new_value))
            if new_value:
                _notify(db, new_value, NotificationType.ASSIGNED,
                        f"You were assigned to bug #{bug.id}: {bug.title}", bug.id, bug.project_id)

    db.commit()
    db.refresh(bug)
    return bug


@router.delete("/{bug_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bug(bug_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.ADMIN)
    db.delete(bug)
    db.commit()
    return None


# --- History ---


@router.get("/{bug_id}/history", response_model=list[BugHistoryOut])
def get_bug_history(bug_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.VIEWER)
    return db.query(BugHistory).filter(BugHistory.bug_id == bug_id).order_by(BugHistory.created_at).all()


# --- Comments ---


@router.get("/{bug_id}/comments", response_model=list[CommentOut])
def list_comments(bug_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.VIEWER)
    return db.query(Comment).filter(Comment.bug_id == bug_id).order_by(Comment.created_at).all()


@router.post("/{bug_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    bug_id: int, payload: CommentCreate,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.REPORTER)

    comment = Comment(bug_id=bug_id, author_id=current_user.id, content=payload.content)
    db.add(comment)
    _log_history(db, bug_id, current_user.id, HistoryActionType.COMMENT_ADDED)

    for uid in {bug.reporter_id, bug.assignee_id} - {current_user.id, None}:
        _notify(db, uid, NotificationType.COMMENTED,
                f"New comment on bug #{bug.id}: {bug.title}", bug.id, bug.project_id)

    db.commit()
    db.refresh(comment)
    return comment


@router.put("/{bug_id}/comments/{comment_id}", response_model=CommentOut)
def edit_comment(
    bug_id: int, comment_id: int, payload: CommentUpdate,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.bug_id == bug_id).first()
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")
    comment.content = payload.content
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{bug_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    bug_id: int, comment_id: int,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.bug_id == bug_id).first()
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    bug = _get_bug_or_404(db, bug_id)
    is_owner = comment.author_id == current_user.id
    if not is_owner:
        check_membership(db, current_user, bug.project_id, ProjectRole.ADMIN)
    db.delete(comment)
    db.commit()
    return None


# --- Attachments ---


@router.get("/{bug_id}/attachments", response_model=list[AttachmentOut])
def list_attachments(bug_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.VIEWER)
    return db.query(Attachment).filter(Attachment.bug_id == bug_id).all()


@router.post("/{bug_id}/attachments", response_model=AttachmentOut, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    bug_id: int, file: UploadFile = File(...),
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.REPORTER)

    bug_dir = os.path.join(UPLOAD_DIR, str(bug_id))
    os.makedirs(bug_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = os.path.join(bug_dir, stored_name)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    size = os.path.getsize(dest_path)

    attachment = Attachment(
        bug_id=bug_id, uploaded_by_id=current_user.id, filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size, storage_path=dest_path,
    )
    db.add(attachment)
    _log_history(db, bug_id, current_user.id, HistoryActionType.ATTACHMENT_ADDED,
                 "attachment", None, file.filename)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.delete("/{bug_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    bug_id: int, attachment_id: int,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.DEVELOPER)
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id, Attachment.bug_id == bug_id
    ).first()
    if attachment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    if os.path.exists(attachment.storage_path):
        os.remove(attachment.storage_path)
    db.delete(attachment)
    db.commit()
    return None


# --- Labels on a bug ---


@router.post("/{bug_id}/labels/{label_id}", response_model=BugOut)
def add_label_to_bug(
    bug_id: int, label_id: int,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.DEVELOPER)
    label = db.query(Label).filter(Label.id == label_id, Label.project_id == bug.project_id).first()
    if label is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label not found")
    if label not in bug.labels:
        bug.labels.append(label)
        _log_history(db, bug.id, current_user.id, HistoryActionType.LABEL_CHANGED,
                     "labels", None, label.name)
        db.commit()
        db.refresh(bug)
    return bug


@router.delete("/{bug_id}/labels/{label_id}", response_model=BugOut)
def remove_label_from_bug(
    bug_id: int, label_id: int,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.DEVELOPER)
    label = db.query(Label).filter(Label.id == label_id).first()
    if label is not None and label in bug.labels:
        bug.labels.remove(label)
        db.commit()
        db.refresh(bug)
    return bug


# --- Relationships / dependencies (what Jeet's service reads) ---


@router.post("/{bug_id}/dependencies", response_model=RelationshipOut, status_code=status.HTTP_201_CREATED)
def add_relationship(
    bug_id: int, payload: RelationshipCreate,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.DEVELOPER)
    _get_bug_or_404(db, payload.related_bug_id)  # ensure target bug exists

    rel = BugRelationship(
        bug_id=bug_id, related_bug_id=payload.related_bug_id,
        relationship_type=payload.relationship_type, created_by_id=current_user.id,
        note=payload.note,
    )
    db.add(rel)
    _log_history(db, bug_id, current_user.id, HistoryActionType.RELATIONSHIP_ADDED,
                 "relationship", None, f"{payload.relationship_type.value} -> #{payload.related_bug_id}")
    db.commit()
    db.refresh(rel)
    return rel


@router.get("/{bug_id}/dependencies", response_model=BugDependencies)
def get_dependencies(bug_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.VIEWER)
    return BugDependencies(
        bug_id=bug_id,
        outgoing=list(bug.outgoing_relationships),
        incoming=list(bug.incoming_relationships),
    )


@router.delete("/{bug_id}/dependencies/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(
    bug_id: int, relationship_id: int,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    bug = _get_bug_or_404(db, bug_id)
    check_membership(db, current_user, bug.project_id, ProjectRole.DEVELOPER)
    rel = db.query(BugRelationship).filter(
        BugRelationship.id == relationship_id, BugRelationship.bug_id == bug_id
    ).first()
    if rel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    db.delete(rel)
    db.commit()
    return None
