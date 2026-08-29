from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MilestoneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    due_date: Optional[date] = None
    is_completed: bool = False


class MilestoneUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    due_date: Optional[date] = None
    is_completed: Optional[bool] = None


class MilestoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    due_date: Optional[date]
    is_completed: bool
