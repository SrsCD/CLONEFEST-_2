from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class VersionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    release_date: Optional[date] = None
    is_released: bool = False


class VersionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    release_date: Optional[date] = None
    is_released: Optional[bool] = None


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    release_date: Optional[date]
    is_released: bool
