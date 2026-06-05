from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Task(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()