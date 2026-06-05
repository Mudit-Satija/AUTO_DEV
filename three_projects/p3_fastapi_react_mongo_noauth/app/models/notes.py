from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    updatedAt: Optional[datetime] = None

class NoteResponse(NoteBase):
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }