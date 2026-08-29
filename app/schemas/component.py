from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ComponentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    owner_id: Optional[int] = None


class ComponentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    owner_id: Optional[int] = None


class ComponentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    description: Optional[str]
    owner_id: Optional[int]
