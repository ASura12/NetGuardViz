from datetime import datetime
from pydantic import BaseModel

class AlertModel(BaseModel):
    filename: str
    detected_keywords: list[str]
    detected_at: datetime
