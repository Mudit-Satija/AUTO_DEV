from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    status: str = "todo"  # todo, in_progress, done
    priority: str = "medium"  # low, medium, high

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class TaskOut(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True