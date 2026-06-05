from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrderBase(BaseModel):
    total_amount: float
    status: str

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None

class OrderOut(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True