from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import ProjectRole
from app.schemas.user import UserOut


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    key: str = Field(min_length=1, max_length=10, pattern=r"^[A-Z][A-Z0-9]*$")
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None
    is_archived: Optional[bool] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    key: str
    description: Optional[str]
    is_archived: bool


class ProjectMemberAdd(BaseModel):
    user_id: int
    role: ProjectRole = ProjectRole.REPORTER


class ProjectMemberRoleUpdate(BaseModel):
    role: ProjectRole


class ProjectMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role: ProjectRole
    user: UserOut
