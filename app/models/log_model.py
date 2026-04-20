from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class LogModel(BaseModel):
    filename: str
    content: str
    uploaded_at: datetime
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None