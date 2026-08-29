from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import BugSeverity, BugPriority, BugStatus


class BugCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str
    assignee_id: Optional[int] = None
    severity: BugSeverity = BugSeverity.MEDIUM
    priority: BugPriority = BugPriority.P2
    component_id: Optional[int] = None
    version_id: Optional[int] = None
    milestone_id: Optional[int] = None
    environment: Optional[str] = None
    reproduction_steps: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    due_date: Optional[date] = None
    is_security: bool = False
    label_ids: list[int] = []


class BugUpdate(BaseModel):
    """Partial update. Any field left out is left unchanged."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    severity: Optional[BugSeverity] = None
    priority: Optional[BugPriority] = None
    status: Optional[BugStatus] = None
    component_id: Optional[int] = None
    version_id: Optional[int] = None
    milestone_id: Optional[int] = None
    environment: Optional[str] = None
    reproduction_steps: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    due_date: Optional[date] = None
    is_security: Optional[bool] = None


class LabelMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    color: str


class BugOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    description: str
    reporter_id: int
    assignee_id: Optional[int]
    severity: BugSeverity
    priority: BugPriority
    status: BugStatus
    component_id: Optional[int]
    version_id: Optional[int]
    milestone_id: Optional[int]
    environment: Optional[str]
    reproduction_steps: Optional[str]
    expected_behavior: Optional[str]
    actual_behavior: Optional[str]
    due_date: Optional[date]
    is_security: bool
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    labels: list[LabelMini] = []

    # Resolved text alongside the IDs above — this is what a text-based
    # classifier (or a human) actually reads. Populated from Bug's
    # computed properties, not stored columns.
    reporter_username: Optional[str] = None
    assignee_username: Optional[str] = None
    component_name: Optional[str] = None
