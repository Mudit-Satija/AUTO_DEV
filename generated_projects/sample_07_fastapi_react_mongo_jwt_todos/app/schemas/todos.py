from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoOut(TodoCreate):
    id: str
    owner: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }