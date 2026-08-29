from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.enums import HistoryActionType, NotificationType


class BugHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bug_id: int
    changed_by_id: int
    action_type: HistoryActionType
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: NotificationType
    message: str
    is_read: bool
    bug_id: Optional[int]
    project_id: Optional[int]
    created_at: datetime
