from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True