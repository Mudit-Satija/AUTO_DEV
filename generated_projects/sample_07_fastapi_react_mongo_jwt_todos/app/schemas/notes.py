from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteOut(NoteCreate):
    id: str
    owner: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }