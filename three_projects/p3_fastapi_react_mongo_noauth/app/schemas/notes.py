from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteInDB(NoteBase):
    id: str
    created_at: datetime
    updated_at: datetime

class Note(NoteInDB):
    pass