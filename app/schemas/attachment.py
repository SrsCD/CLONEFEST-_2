from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bug_id: int
    uploaded_by_id: int
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime
